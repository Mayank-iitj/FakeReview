"""Pydantic schemas for API requests/responses."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ReviewRequest(BaseModel):
    """Review check request."""
    text: str
    rating: float
    platform: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReviewResponse(BaseModel):
    """Review classification response."""
    review_id: int
    fake_probability: float
    is_fake: bool
    confidence: float
    reasons: List[str]


class BatchResponse(BaseModel):
    """Batch processing response."""
    total_reviews: int
    fake_count: int
    genuine_count: int
    results: List[Dict[str, Any]]
