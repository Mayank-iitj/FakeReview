"""Unit tests for the fake review detection system."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Mock imports to avoid dependency errors during testing
class MockSession:
    """Mock database session."""
    pass


@pytest.fixture
def sample_reviews():
    """Sample reviews for testing."""
    return pd.DataFrame([
        {
            'review_text': 'This is an excellent product! Best purchase ever! Highly recommend!!!',
            'rating': 5.0,
            'reviewer_name': 'User123',
            'platform': 'amazon'
        },
        {
            'review_text': 'Terrible product. Waste of money. Do not buy!',
            'rating': 1.0,
            'reviewer_name': 'User456',
            'platform': 'amazon'
        },
        {
            'review_text': 'Great quality and fast shipping. Very satisfied with my purchase.',
            'rating': 4.5,
            'reviewer_name': 'User789',
            'platform': 'flipkart'
        },
    ])


class TestPreprocessor:
    """Tests for ReviewPreprocessor."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        from app.preprocessing import ReviewPreprocessor
        
        preprocessor = ReviewPreprocessor()
        
        # Test URL removal
        text = "Check this out: http://example.com"
        cleaned = preprocessor.clean_text(text)
        assert "http" not in cleaned
        
        # Test lowercasing
        text = "HELLO World"
        cleaned = preprocessor.clean_text(text)
        assert cleaned == cleaned.lower()
    
    def test_tokenization(self):
        """Test text tokenization."""
        from app.preprocessing import ReviewPreprocessor
        
        preprocessor = ReviewPreprocessor()
        text = "This is a test"
        tokens = preprocessor.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
    
    def test_feature_extraction(self):
        """Test feature extraction."""
        from app.preprocessing import ReviewPreprocessor
        
        preprocessor = ReviewPreprocessor()
        text = "Great product! Very happy with my purchase."
        rating = 5.0
        
        features = preprocessor.extract_features(text, rating)
        
        assert 'text_length' in features
        assert 'word_count' in features
        assert 'rating' in features
        assert 'sentiment_rating_diff' in features
        assert features['rating'] == 5.0


class TestClassifier:
    """Tests for FakeReviewClassifier."""
    
    def test_classifier_initialization(self):
        """Test classifier initialization."""
        from app.classifier import FakeReviewClassifier
        
        classifier = FakeReviewClassifier()
        
        assert classifier.rf_model is not None
        assert classifier.xgb_model is not None
        assert classifier.svm_model is not None
        assert classifier.vectorizer is not None
    
    def test_prediction_structure(self):
        """Test prediction output structure."""
        from app.classifier import FakeReviewClassifier
        
        classifier = FakeReviewClassifier()
        
        # Mock prediction
        result = {
            'fake_probability': 0.7,
            'is_fake': True,
            'confidence': 0.4,
            'model_probabilities': {
                'random_forest': 0.7,
                'xgboost': 0.8,
                'svm': 0.6
            },
            'reasons': ['Contains spam phrases']
        }
        
        assert 'fake_probability' in result
        assert 'is_fake' in result
        assert 'confidence' in result
        assert 'reasons' in result
        assert 0 <= result['fake_probability'] <= 1


class TestScrapers:
    """Tests for web scrapers."""
    
    def test_amazon_scraper_init(self):
        """Test Amazon scraper initialization."""
        from app.scraper import AmazonScraper
        
        scraper = AmazonScraper()
        
        assert scraper.base_url == "https://www.amazon.com"
        assert scraper.timeout > 0
    
    def test_flipkart_scraper_init(self):
        """Test Flipkart scraper initialization."""
        from app.scraper import FlipkartScraper
        
        scraper = FlipkartScraper()
        
        assert scraper.base_url == "https://www.flipkart.com"
        assert scraper.timeout > 0


class TestDatabase:
    """Tests for database models."""
    
    def test_review_model_creation(self):
        """Test review model."""
        from app.models import Review, ReviewStatus
        
        review = Review(
            platform='amazon',
            product_id='B001',
            review_text='Test review',
            rating=5.0,
            status=ReviewStatus.GENUINE
        )
        
        assert review.platform == 'amazon'
        assert review.rating == 5.0
        assert review.status == ReviewStatus.GENUINE
    
    def test_flag_model_creation(self):
        """Test flag model."""
        from app.models import Flag
        
        flag = Flag(
            review_id=1,
            flag_type='spam',
            reason='Contains spam indicators',
            confidence=0.85
        )
        
        assert flag.review_id == 1
        assert flag.flag_type == 'spam'
        assert flag.confidence == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
