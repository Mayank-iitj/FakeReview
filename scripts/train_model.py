"""Train fake review classifier models."""
import pandas as pd
import numpy as np
from loguru import logger
import os

from app.classifier import FakeReviewClassifier
from app.config import settings


def generate_sample_data():
    """Generate sample training data for demonstration."""
    logger.info("Generating sample training data...")
    
    # Real reviews (genuine)
    genuine_reviews = [
        "Great product! Exactly as described. Fast shipping.",
        "Very happy with this purchase. Good quality and value for money.",
        "Perfect! Works as expected. Highly recommend.",
        "Excellent customer service and product quality.",
        "Best purchase I've made in a while. Really satisfied.",
        "Good quality, fair price. Will buy again.",
        "Arrived quickly and in perfect condition.",
        "This product exceeded my expectations.",
        "Great value for the price. Works perfectly.",
        "Exactly what I was looking for. Very pleased.",
        "Outstanding quality and service.",
        "Highly satisfied with my purchase.",
        "This is a solid, reliable product.",
        "Great purchase, no regrets.",
        "Product is as described and works great.",
    ]
    
    # Suspicious reviews (fake)
    fake_reviews = [
        "BEST PRODUCT EVER!!! BUY NOW!!! CLICK HERE!!!",
        "Amazing!!! This changed my life completely!!!",
        "I bought 5 of these!!! Everyone should have one!!!",
        "Best deal ever! Limited time offer! Free shipping!",
        "Perfect product! 10000% recommend!!!",
        "This is the BEST product I have EVER seen!",
        "You MUST buy this NOW! Don't wait!",
        "Revolutionary product! Buy now and save!",
        "THIS IS AMAZING!!! GET IT NOW!!!",
        "Best thing ever! Highly recommend to everyone!!!",
        "5 stars! Best purchase! Must buy!",
        "Incredible! Everyone should have this!",
        "Amazing product! Best deal ever!",
        "Love it! Recommend to all friends!",
        "Perfect! Best product! 5 stars!",
    ]
    
    # Mismatched sentiment (ratings don't match text)
    mismatched_reviews = [
        "This product is absolutely useless and broke immediately.",  # 5 stars
        "Complete waste of money, terrible quality.",  # 5 stars
        "Worst purchase ever, do not recommend.",  # 5 stars
        "Broken on arrival, customer service ignored me.",  # 5 stars
        "This is the worst product I've ever bought.",  # 5 stars
    ]
    
    # Create training data
    genuine_data = [(text, np.random.uniform(3, 5), 0) for text in genuine_reviews]
    fake_data = [(text, np.random.uniform(4.5, 5), 1) for text in fake_reviews]
    mismatched_data = [(text, 5.0, 1) for text in mismatched_reviews]
    
    all_data = genuine_data + fake_data + mismatched_data
    
    df = pd.DataFrame(all_data, columns=['review_text', 'rating', 'label'])
    
    return df


def train_model():
    """Train the fake review classifier."""
    logger.info("Starting model training...")
    
    # Generate sample data
    df = generate_sample_data()
    logger.info(f"Training data: {len(df)} reviews ({df['label'].sum()} fake, {(1-df['label']).sum().astype(int)} genuine)")
    
    # Initialize classifier
    classifier = FakeReviewClassifier()
    
    # Extract features
    features, processed_df = classifier.extract_features(df)
    
    # Get labels
    y = df['label'].values
    
    # Train models
    metrics = classifier.train(features, y)
    
    # Print metrics
    logger.info("\n" + "="*60)
    logger.info("MODEL PERFORMANCE METRICS")
    logger.info("="*60)
    
    for model_name, model_metrics in metrics.items():
        logger.info(f"\n{model_name.upper()}")
        logger.info(f"  Accuracy:  {model_metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {model_metrics['precision']:.4f}")
        logger.info(f"  Recall:    {model_metrics['recall']:.4f}")
        logger.info(f"  F1-Score:  {model_metrics['f1_score']:.4f}")
        logger.info(f"  ROC-AUC:   {model_metrics['roc_auc']:.4f}")
    
    logger.info("\n" + "="*60)
    
    # Save models
    classifier.save()
    logger.info("✓ Models saved successfully")
    
    return classifier, metrics


def main():
    """Main training function."""
    logger.info("Fake Review Classifier - Model Training")
    logger.info("-" * 60)
    
    # Train model
    classifier, metrics = train_model()
    
    logger.info("\n✓ Training complete!")
    logger.info(f"✓ Models saved to: {classifier.model_path}")
    
    # Test predictions
    logger.info("\n" + "="*60)
    logger.info("EXAMPLE PREDICTIONS")
    logger.info("="*60)
    
    test_reviews = [
        ("This product is amazing! Highly recommend!!!", 5.0, "Suspicious review"),
        ("Great quality and fast shipping. Very satisfied.", 4.5, "Genuine review"),
        ("Terrible product, waste of money.", 1.0, "Negative but likely genuine"),
    ]
    
    for text, rating, description in test_reviews:
        logger.info(f"\nTesting: {description}")
        logger.info(f"Text: '{text}'")
        logger.info(f"Rating: {rating}")
        
        result = classifier.predict(text, rating)
        
        logger.info(f"Fake Probability: {result['fake_probability']:.2%}")
        logger.info(f"Is Fake: {result['is_fake']}")
        logger.info(f"Reasons:")
        for reason in result['reasons']:
            logger.info(f"  - {reason}")


if __name__ == "__main__":
    main()
