"""Demo data generator for testing."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

from app.preprocessing import ReviewPreprocessor


def generate_demo_dataset(n_reviews=100):
    """
    Generate a demo dataset with mixed genuine and fake reviews.
    
    Args:
        n_reviews: Number of reviews to generate
        
    Returns:
        DataFrame with demo reviews
    """
    
    genuine_templates = [
        "Great product! Works as advertised.",
        "Very satisfied with my purchase.",
        "Good quality for the price.",
        "Fast delivery and excellent product.",
        "Exactly what I needed, very happy.",
        "Highly recommend this product.",
        "Excellent service and quality.",
        "Will definitely buy again.",
        "Perfect! Just what I was looking for.",
        "Amazing product, great value.",
    ]
    
    fake_templates = [
        "BEST PRODUCT EVER!!! BUY NOW!!!",
        "This changed my life!!! 5 STARS!!!",
        "AMAZING!!! Everyone needs this!!!",
        "Best deal ever! Limited time only!!!",
        "YOU MUST BUY THIS NOW!!!",
        "INCREDIBLE!!! Highly recommend!!!",
        "BEST PURCHASE! 100% recommend!!!",
        "AMAZING QUALITY!!! Best ever!!!",
        "MUST HAVE!!! Perfect product!!!",
        "EXCELLENT!!! Buy it now!!!",
    ]
    
    reviews = []
    
    for i in range(n_reviews):
        # 70% genuine, 30% fake
        is_fake = random.random() < 0.3
        
        if is_fake:
            template = random.choice(fake_templates)
            rating = random.choice([4.5, 5.0])
            status = 'fake'
        else:
            template = random.choice(genuine_templates)
            rating = random.uniform(2, 5)
            status = 'genuine'
        
        # Add some variations
        text = template + " " + random.choice([
            "Great!",
            "Perfect!",
            "Excellent!",
            "Amazing!",
            "Wonderful!",
            ""
        ])
        
        review = {
            'id': i + 1,
            'platform': random.choice(['amazon', 'flipkart']),
            'product_id': f'PROD{random.randint(1000, 9999)}',
            'product_name': f'Product {random.randint(1, 20)}',
            'review_text': text,
            'rating': rating,
            'reviewer_name': f'User{random.randint(1000, 9999)}',
            'verified_purchase': random.random() > 0.3,
            'helpful_count': random.randint(0, 50),
            'status': status,
            'scraped_at': datetime.now() - timedelta(days=random.randint(1, 30))
        }
        
        reviews.append(review)
    
    df = pd.DataFrame(reviews)
    
    return df


def generate_sample_csv(filename='data/sample_reviews.csv', n_reviews=50):
    """
    Generate sample CSV for batch processing demo.
    
    Args:
        filename: Output CSV file path
        n_reviews: Number of reviews to generate
    """
    # Create data directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    reviews = []
    
    for i in range(n_reviews):
        is_fake = random.random() < 0.3
        
        if is_fake:
            text = random.choice([
                "BEST PRODUCT EVER!!! BUY NOW!!!",
                "This changed my life!!! 5 STARS!!!",
                "AMAZING!!! Everyone needs this!!!",
            ])
            rating = 5.0
        else:
            text = random.choice([
                "Great product! Works as advertised.",
                "Very satisfied with my purchase.",
                "Good quality for the price.",
            ])
            rating = random.uniform(2, 5)
        
        reviews.append({
            'text': text,
            'rating': rating,
            'product_id': f'PROD{random.randint(1000, 9999)}',
            'platform': random.choice(['amazon', 'flipkart'])
        })
    
    df = pd.DataFrame(reviews)
    df.to_csv(filename, index=False)
    
    print(f"✓ Sample CSV generated: {filename}")


if __name__ == "__main__":
    # Generate demo dataset
    print("Generating demo dataset...")
    df = generate_demo_dataset(100)
    print(f"✓ Generated {len(df)} reviews")
    print(f"  - Fake: {(df['status'] == 'fake').sum()}")
    print(f"  - Genuine: {(df['status'] == 'genuine').sum()}")
    
    # Generate sample CSV
    print("\nGenerating sample CSV for batch processing...")
    generate_sample_csv()
    
    print("\n✓ Demo data generation complete!")
