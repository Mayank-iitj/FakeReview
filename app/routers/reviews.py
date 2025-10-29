"""Review API endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from loguru import logger

from app.database import get_db
from app.models import Review, ReviewStatus
from app.classifier import FakeReviewClassifier
from app.schemas import ReviewRequest, ReviewResponse, BatchResponse

router = APIRouter()
classifier = FakeReviewClassifier()

# Try to load pre-trained model
try:
    classifier.load()
except Exception as e:
    logger.warning(f"Could not load pre-trained model: {e}")


@router.post("/check", response_model=ReviewResponse)
async def check_review(
    request: ReviewRequest,
    db: Session = Depends(get_db)
) -> ReviewResponse:
    """
    Check if a single review is fake.
    
    Args:
        request: Review check request
        db: Database session
        
    Returns:
        Review classification result
    """
    logger.info(f"Checking review: rating={request.rating}")
    
    # Make prediction
    prediction = classifier.predict(
        review_text=request.text,
        rating=request.rating,
        metadata=request.metadata
    )
    
    # Save to database
    review = Review(
        platform=request.platform or "api",
        product_id=request.product_id or "unknown",
        product_name=request.product_name,
        review_text=request.text,
        rating=request.rating,
        status=ReviewStatus.FAKE if prediction['is_fake'] else ReviewStatus.GENUINE,
        fake_probability=prediction['fake_probability'],
        trust_score=1 - prediction['fake_probability']
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return ReviewResponse(
        review_id=review.id,
        fake_probability=prediction['fake_probability'],
        is_fake=prediction['is_fake'],
        confidence=prediction['confidence'],
        reasons=prediction['reasons']
    )


@router.post("/batch", response_model=BatchResponse)
async def batch_check(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> BatchResponse:
    """
    Batch check multiple reviews from CSV file.
    
    Expected CSV columns: text, rating, product_id, platform
    
    Args:
        file: CSV file with reviews
        db: Database session
        
    Returns:
        Batch processing result
    """
    logger.info(f"Processing batch file: {file.filename}")
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = ['text', 'rating']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_cols)}"
            )
        
        # Process each review
        results = []
        for idx, row in df.iterrows():
            try:
                prediction = classifier.predict(
                    review_text=row['text'],
                    rating=float(row['rating'])
                )
                
                # Save to database
                review = Review(
                    platform=row.get('platform', 'batch_upload'),
                    product_id=row.get('product_id', 'unknown'),
                    review_text=row['text'],
                    rating=float(row['rating']),
                    status=ReviewStatus.FAKE if prediction['is_fake'] else ReviewStatus.GENUINE,
                    fake_probability=prediction['fake_probability']
                )
                
                db.add(review)
                results.append({
                    'index': idx,
                    'fake_probability': prediction['fake_probability'],
                    'is_fake': prediction['is_fake'],
                    'confidence': prediction['confidence']
                })
            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                results.append({'index': idx, 'error': str(e)})
        
        db.commit()
        
        # Statistics
        fake_count = sum(1 for r in results if r.get('is_fake', False))
        
        logger.info(f"Batch processing complete: {len(results)} reviews, {fake_count} flagged as fake")
        
        return BatchResponse(
            total_reviews=len(results),
            fake_count=fake_count,
            genuine_count=len(results) - fake_count,
            results=results
        )
    
    except Exception as e:
        logger.error(f"Error processing batch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[ReviewResponse])
async def list_reviews(
    platform: Optional[str] = None,
    status: Optional[ReviewStatus] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ReviewResponse]:
    """
    List reviews with optional filtering.
    
    Args:
        platform: Filter by platform
        status: Filter by status
        limit: Maximum results
        db: Database session
        
    Returns:
        List of reviews
    """
    query = db.query(Review)
    
    if platform:
        query = query.filter(Review.platform == platform)
    
    if status:
        query = query.filter(Review.status == status)
    
    reviews = query.limit(limit).all()
    
    return [
        ReviewResponse(
            review_id=r.id,
            fake_probability=r.fake_probability or 0,
            is_fake=r.status == ReviewStatus.FAKE,
            confidence=0,
            reasons=[]
        )
        for r in reviews
    ]


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID."""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {
        'id': review.id,
        'platform': review.platform,
        'product_name': review.product_name,
        'review_text': review.review_text,
        'rating': review.rating,
        'reviewer_name': review.reviewer_name,
        'status': review.status,
        'fake_probability': review.fake_probability,
        'trust_score': review.trust_score,
        'scraped_at': review.scraped_at
    }
