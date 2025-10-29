"""Admin API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from loguru import logger

from app.database import get_db
from app.models import Review, ReviewStatus, Flag, DeletionRequest, DeletionStatus

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get dashboard statistics.
    
    Returns:
        Dictionary with system statistics
    """
    total_reviews = db.query(func.count(Review.id)).scalar() or 0
    fake_reviews = db.query(func.count(Review.id)).filter(
        Review.status == ReviewStatus.FAKE
    ).scalar() or 0
    genuine_reviews = db.query(func.count(Review.id)).filter(
        Review.status == ReviewStatus.GENUINE
    ).scalar() or 0
    flagged_reviews = db.query(func.count(Review.id)).filter(
        Review.status == ReviewStatus.FLAGGED
    ).scalar() or 0
    removed_reviews = db.query(func.count(Review.id)).filter(
        Review.status == ReviewStatus.REMOVED
    ).scalar() or 0
    
    pending_deletions = db.query(func.count(DeletionRequest.id)).filter(
        DeletionRequest.status == DeletionStatus.PENDING
    ).scalar() or 0
    
    avg_trust_score = db.query(func.avg(Review.trust_score)).scalar() or 0
    
    return {
        'total_reviews': total_reviews,
        'fake_reviews': fake_reviews,
        'genuine_reviews': genuine_reviews,
        'flagged_reviews': flagged_reviews,
        'removed_reviews': removed_reviews,
        'fake_percentage': (fake_reviews / total_reviews * 100) if total_reviews > 0 else 0,
        'pending_deletions': pending_deletions,
        'average_trust_score': float(avg_trust_score)
    }


@router.get("/flagged-reviews")
async def get_flagged_reviews(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get reviews flagged as suspicious.
    
    Args:
        limit: Maximum results
        db: Database session
        
    Returns:
        List of flagged reviews
    """
    reviews = db.query(Review).filter(
        Review.status == ReviewStatus.FLAGGED
    ).order_by(Review.updated_at.desc()).limit(limit).all()
    
    results = []
    for review in reviews:
        flags = db.query(Flag).filter(Flag.review_id == review.id).all()
        results.append({
            'id': review.id,
            'product_name': review.product_name,
            'reviewer_name': review.reviewer_name,
            'review_text': review.review_text[:100],
            'rating': review.rating,
            'fake_probability': review.fake_probability,
            'flags': [
                {
                    'type': f.flag_type,
                    'reason': f.reason,
                    'confidence': f.confidence
                }
                for f in flags
            ],
            'flagged_at': review.updated_at
        })
    
    return results


@router.post("/reviews/{review_id}/flag")
async def flag_review(
    review_id: int,
    reason: str,
    flag_type: str = "manual",
    db: Session = Depends(get_db)
):
    """
    Manually flag a review.
    
    Args:
        review_id: Review ID
        reason: Reason for flagging
        flag_type: Type of flag
        db: Database session
        
    Returns:
        Success response
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    flag = Flag(
        review_id=review_id,
        flag_type=flag_type,
        reason=reason,
        auto_flagged=False,
        flagged_by="admin"
    )
    
    review.status = ReviewStatus.FLAGGED
    db.add(flag)
    db.commit()
    
    logger.info(f"Review {review_id} flagged with reason: {reason}")
    
    return {'status': 'success', 'message': f'Review {review_id} flagged'}


@router.post("/reviews/{review_id}/override")
async def override_classification(
    review_id: int,
    new_status: ReviewStatus,
    db: Session = Depends(get_db)
):
    """
    Override ML classification for a review.
    
    Args:
        review_id: Review ID
        new_status: New status
        db: Database session
        
    Returns:
        Success response
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    old_status = review.status
    review.status = new_status
    db.commit()
    
    logger.info(f"Review {review_id} status changed from {old_status} to {new_status}")
    
    return {'status': 'success', 'message': f'Review reclassified to {new_status}'}


@router.post("/reviews/{review_id}/request-deletion")
async def request_deletion(
    review_id: int,
    db: Session = Depends(get_db)
):
    """
    Request deletion for a review.
    
    Args:
        review_id: Review ID
        db: Database session
        
    Returns:
        Deletion request details
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if deletion request already exists
    existing = db.query(DeletionRequest).filter(
        DeletionRequest.review_id == review_id,
        DeletionRequest.status.in_([DeletionStatus.PENDING, DeletionStatus.SUBMITTED])
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Deletion request already exists for this review"
        )
    
    deletion_request = DeletionRequest(
        review_id=review_id,
        status=DeletionStatus.PENDING,
        requested_by='admin'
    )
    
    db.add(deletion_request)
    db.commit()
    db.refresh(deletion_request)
    
    logger.info(f"Deletion requested for review {review_id}")
    
    return {
        'deletion_request_id': deletion_request.id,
        'status': deletion_request.status,
        'created_at': deletion_request.created_at
    }


@router.get("/deletion-requests")
async def get_deletion_requests(
    status: str = "pending",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get deletion requests.
    
    Args:
        status: Filter by status
        limit: Maximum results
        db: Database session
        
    Returns:
        List of deletion requests
    """
    query = db.query(DeletionRequest)
    
    if status:
        query = query.filter(DeletionRequest.status == status)
    
    requests = query.order_by(DeletionRequest.created_at.desc()).limit(limit).all()
    
    return [
        {
            'id': r.id,
            'review_id': r.review_id,
            'status': r.status,
            'created_at': r.created_at,
            'approved_at': r.approved_at
        }
        for r in requests
    ]
