"""
Test script for URL Analysis feature
This demonstrates how to use the web scraper programmatically
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.web_scraper import ReviewScraper, scrape_product_reviews
from src.prediction import ReviewPredictor
from src import config
import pandas as pd


def demo_url_analysis():
    """
    Demonstrate URL analysis feature with a sample product.
    
    Note: This is a demonstration. Actual scraping results depend on:
    - Website structure (may change)
    - Anti-scraping measures
    - Network connectivity
    - Platform terms of service
    """
    
    print("=" * 60)
    print("Fake Review Detector - URL Analysis Demo")
    print("=" * 60)
    print()
    
    # Example URLs (for demonstration - results may vary)
    test_urls = {
        "Amazon Example": "https://www.amazon.com/dp/B0B9QS5FZH",  # Example ASIN
        "Note": "Replace with actual product URL for real testing"
    }
    
    print("Test URLs:")
    for name, url in test_urls.items():
        print(f"  {name}: {url}")
    print()
    
    # Get user input or use demo URL
    print("Enter a product URL to analyze (or press Enter to skip scraping):")
    user_url = input("> ").strip()
    
    if not user_url:
        print("\nSkipping live scraping demo.")
        print("Creating sample data for demonstration...")
        
        # Create sample reviews for demonstration
        sample_reviews = [
            {
                'text': 'Amazing product! Best purchase ever! Five stars! Highly recommend!',
                'rating': '5.0 out of 5 stars',
                'date': 'October 15, 2025',
                'platform': 'Demo'
            },
            {
                'text': 'Product is okay. Does what it says. Shipping was a bit slow but overall satisfied.',
                'rating': '4.0 out of 5 stars',
                'date': 'October 20, 2025',
                'platform': 'Demo'
            },
            {
                'text': 'Perfect!!! Excellent quality!!! Must buy!!! Amazing deal!!!',
                'rating': '5.0 out of 5 stars',
                'date': 'October 22, 2025',
                'platform': 'Demo'
            }
        ]
        
        reviews_df = pd.DataFrame(sample_reviews)
        print(f"✓ Created {len(reviews_df)} sample reviews")
        
    else:
        print(f"\nAnalyzing URL: {user_url}")
        print("-" * 60)
        
        # Initialize scraper
        print("Initializing scraper...")
        scraper = ReviewScraper(max_reviews=20, delay=1.5)
        
        # Identify platform
        platform = scraper.identify_platform(user_url)
        if not platform:
            print("✗ Unsupported platform!")
            print("Supported platforms: Amazon, Flipkart, eBay")
            return
        
        print(f"✓ Detected platform: {platform.title()}")
        
        # Scrape reviews
        print(f"Scraping reviews... (max: 20)")
        try:
            reviews = scraper.scrape_reviews(user_url)
            
            if not reviews:
                print("✗ No reviews found!")
                print("\nPossible reasons:")
                print("  - Product has no reviews")
                print("  - Website structure changed")
                print("  - Anti-scraping measures")
                print("  - Network issues")
                return
            
            reviews_df = scraper.reviews_to_dataframe(reviews)
            print(f"✓ Scraped {len(reviews_df)} reviews")
            
        except Exception as e:
            print(f"✗ Error scraping: {str(e)}")
            return
    
    print()
    print("-" * 60)
    print("Review Preview:")
    print("-" * 60)
    print(reviews_df[['text', 'rating']].head())
    print()
    
    # Analyze reviews
    print("-" * 60)
    print("Analyzing reviews with ML model...")
    print("-" * 60)
    
    try:
        # Load predictor
        predictor = ReviewPredictor()
        predictor.load_model(
            str(config.BEST_MODEL_PATH),
            str(config.VECTORIZER_PATH),
            str(config.LABEL_ENCODER_PATH)
        )
        print("✓ Model loaded")
        
        # Make predictions
        results_df = predictor.predict_from_dataframe(reviews_df, 'text')
        print("✓ Analysis complete")
        print()
        
        # Display results
        print("=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        total = len(results_df)
        fake_count = (results_df['predicted_label'] == config.FAKE_LABEL).sum()
        genuine_count = (results_df['predicted_label'] == config.GENUINE_LABEL).sum()
        fake_percentage = (fake_count / total * 100) if total > 0 else 0
        avg_confidence = results_df['prediction_confidence'].mean()
        
        print(f"Total Reviews: {total}")
        print(f"Fake Reviews: {fake_count} ({fake_percentage:.1f}%)")
        print(f"Genuine Reviews: {genuine_count} ({100-fake_percentage:.1f}%)")
        print(f"Avg Confidence: {avg_confidence:.1%}")
        print()
        
        # Assessment
        if fake_percentage > 30:
            print("🚨 HIGH ALERT: High percentage of fake reviews!")
        elif fake_percentage > 15:
            print("⚠️  CAUTION: Moderate fake review presence")
        else:
            print("✅ GOOD: Low fake review presence")
        
        print()
        print("-" * 60)
        print("Detailed Results:")
        print("-" * 60)
        
        for idx, row in results_df.iterrows():
            label = "FAKE" if row['predicted_label'] == config.FAKE_LABEL else "GENUINE"
            confidence = row['prediction_confidence']
            text_preview = row['text'][:80] + "..." if len(row['text']) > 80 else row['text']
            
            print(f"\nReview {idx+1}: [{label}] ({confidence:.1%} confidence)")
            print(f"  {text_preview}")
        
        print()
        print("=" * 60)
        
        # Save results
        output_file = "demo_analysis_results.csv"
        results_df.to_csv(output_file, index=False)
        print(f"✓ Results saved to: {output_file}")
        print()
        
    except Exception as e:
        print(f"✗ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("Demo complete!")


if __name__ == "__main__":
    demo_url_analysis()
