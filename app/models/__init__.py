"""Database models."""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class ReviewStatus(str, enum.Enum):
    """Review status enumeration."""
    PENDING = "pending"
    GENUINE = "genuine"
    FAKE = "fake"
    FLAGGED = "flagged"
    REMOVED = "removed"


class DeletionStatus(str, enum.Enum):
    """Deletion request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    FAILED = "failed"


class Review(Base):
    """Review model."""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(500))
    product_url = Column(Text)
    
    review_id = Column(String(100), unique=True, index=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    review_title = Column(String(500))
    
    reviewer_name = Column(String(200))
    reviewer_id = Column(String(100), index=True)
    reviewer_profile_url = Column(Text)
    
    review_date = Column(DateTime)
    verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    location = Column(String(100))
    
    # Classification
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, index=True)
    fake_probability = Column(Float)
    trust_score = Column(Float)
    sentiment_score = Column(Float)
    
    # Features for ML
    features = Column(JSON)
    
    # Timestamps
    scraped_at = Column(DateTime, default=func.now())
    classified_at = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    flags = relationship("Flag", back_populates="review", cascade="all, delete-orphan")
    deletion_requests = relationship("DeletionRequest", back_populates="review")


class Flag(Base):
    """Review flag model."""
    __tablename__ = "flags"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    
    flag_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    confidence = Column(Float)
    
    auto_flagged = Column(Boolean, default=True)
    flagged_by = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="flags")


class DeletionRequest(Base):
    """Deletion request model."""
    __tablename__ = "deletion_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    
    status = Column(SQLEnum(DeletionStatus), default=DeletionStatus.PENDING, index=True)
    platform_response = Column(JSON)
    error_message = Column(Text)
    
    requested_by = Column(String(100))
    approved_by = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    approved_at = Column(DateTime)
    submitted_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    review = relationship("Review", back_populates="deletion_requests")


class User(Base):
    """User model for admin dashboard."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    full_name = Column(String(200))
    role = Column(String(50), default="analyst")  # analyst, admin
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)


class ReviewerProfile(Base):
    """Reviewer profile for behavior analysis."""
    __tablename__ = "reviewer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    
    reviewer_name = Column(String(200))
    total_reviews = Column(Integer, default=0)
    average_rating = Column(Float)
    
    review_frequency = Column(Float)  # reviews per day
    account_age_days = Column(Integer)
    verified_purchases_count = Column(Integer, default=0)
    
    suspicious_patterns = Column(JSON)
    trust_score = Column(Float)
    
    first_seen = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class IPCluster(Base):
    """IP address clustering for spam detection."""
    __tablename__ = "ip_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    
    review_count = Column(Integer, default=0)
    unique_reviewers = Column(Integer, default=0)
    fake_review_count = Column(Integer, default=0)
    
    is_suspicious = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    
    location = Column(String(100))
    isp = Column(String(200))
    
    first_seen = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
