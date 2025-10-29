# URL Analysis Feature Guide

## Overview

The **URL Analysis** feature allows users to automatically scrape and analyze product reviews directly from e-commerce platform URLs. This feature provides comprehensive insights into the authenticity of reviews for any product.

## Supported Platforms

### Currently Supported:
- **Amazon** (amazon.com, amazon.in, amazon.co.uk, amazon.de, amazon.fr, etc.)
- **Flipkart** (flipkart.com)
- **eBay** (ebay.com, ebay.in, ebay.co.uk) - Basic support

## How It Works

1. **User provides product URL**: Simply paste the product link from a supported e-commerce platform
2. **Web Scraping**: The system automatically extracts reviews using BeautifulSoup
3. **ML Analysis**: Each scraped review is analyzed using the trained fake review detection model
4. **Visual Dashboard**: Results are displayed with charts, metrics, and detailed breakdowns

## Key Features

### 1. Automatic Review Extraction
- Scrapes up to 100 reviews per product
- Extracts review text, ratings, and dates
- Handles pagination automatically
- Respectful scraping with configurable delays

### 2. Comprehensive Analysis
- **Overall Metrics**: Total, fake, and genuine review counts
- **Percentage Breakdown**: Visual representation of fake vs. genuine reviews
- **Confidence Scores**: Average confidence levels for predictions
- **Alert System**: 
  - 🚨 High Alert (>30% fake)
  - ⚠️ Caution (15-30% fake)
  - ✅ Good (<15% fake)

### 3. Visual Analytics
- **Pie Chart**: Distribution of fake vs. genuine reviews
- **Histogram**: Confidence score distribution
- **Interactive Filters**: View all, only fake, or only genuine reviews
- **Top Suspicious**: Highlights most suspicious reviews

### 4. Export Capability
- Download complete analysis as CSV
- Includes all review texts, predictions, and confidence scores
- Timestamped filenames for record-keeping

## Usage Instructions

### Step 1: Navigate to URL Analysis
- Open the app
- Select "🔗 URL Analysis" from the sidebar navigation

### Step 2: Enter Product URL
```
Example URLs:
- Amazon: https://www.amazon.com/dp/B07XYZ123
- Flipkart: https://www.flipkart.com/product/...
- eBay: https://www.ebay.com/itm/...
```

### Step 3: Configure Settings
- **Max Reviews**: Choose how many reviews to analyze (10-100)
- Default: 50 reviews

### Step 4: Analyze
- Click "🔍 Scrape & Analyze Reviews"
- Wait for scraping to complete (may take 30-60 seconds)
- View comprehensive results

## Results Interpretation

### Overall Assessment

**High Alert (>30% fake reviews)**
```
⚠️ This product may have suspicious review activity
❌ Consider alternative products
🔍 Research the seller and product more carefully
```

**Caution (15-30% fake reviews)**
```
⚠️ Moderate fake review presence
⚡ Review with some skepticism
📊 Look at genuine reviews specifically
```

**Good (<15% fake reviews)**
```
✅ Trustworthy review profile
👍 Safe to consider this product
💚 Low fake review presence
```

### Confidence Scores
- **High Confidence (>90%)**: Very reliable prediction
- **Medium Confidence (70-90%)**: Reliable prediction
- **Low Confidence (<70%)**: Less certain, review manually

## Technical Details

### Web Scraping Implementation
```python
# Located in: src/web_scraper.py

class ReviewScraper:
    - identify_platform(): Detects e-commerce platform
    - scrape_reviews(): Extracts reviews from product page
    - _scrape_amazon(): Amazon-specific scraping logic
    - _scrape_flipkart(): Flipkart-specific scraping logic
    - reviews_to_dataframe(): Converts to pandas DataFrame
```

### Dependencies
```
requests==2.31.0        # HTTP requests
beautifulsoup4==4.12.3  # HTML parsing
lxml==5.1.0            # Fast XML/HTML parser
```

### Rate Limiting
- Default delay: 1.5 seconds between requests
- Respects robots.txt (in production)
- Maximum 5 pages per scraping session
- Configurable timeout: 10 seconds

## Important Notes

### Legal & Ethical Considerations

⚠️ **Terms of Service**: Web scraping may violate platform terms of service
📚 **Educational Use**: This feature is for educational/research purposes
🤖 **robots.txt**: Always respect robots.txt in production
⚖️ **Fair Use**: Use responsibly and ethically

### Production Recommendations

For production use, consider:

1. **Official APIs**: Use platform-provided APIs when available
   - Amazon Product Advertising API
   - eBay Developer Program
   - Other official data sources

2. **Legal Review**: Consult legal counsel for compliance
3. **Rate Limiting**: Implement stricter rate limits
4. **User Agents**: Use proper user agent strings
5. **Caching**: Cache results to reduce requests

### Troubleshooting

**No reviews found:**
- Check if product URL is correct
- Verify product has reviews
- Platform may have changed HTML structure
- Anti-scraping measures may be active

**Scraping errors:**
- Network connectivity issues
- Website structure changes
- Rate limiting by platform
- Try again later or use Batch Prediction with CSV

**Low confidence scores:**
- May need more training data
- Review text might be ambiguous
- Check for unusual review patterns

## Example Use Case

### Scenario: Evaluating a Popular Product

```
Product: XYZ Wireless Headphones
URL: https://www.amazon.com/dp/B08ABC123

Analysis Results:
- Total Reviews: 50
- Fake Reviews: 8 (16%)
- Genuine Reviews: 42 (84%)
- Average Confidence: 92%
- Assessment: ⚠️ Caution

Action: Review genuine reviews specifically before purchase
```

## Future Enhancements

Planned improvements:
- [ ] Support for more platforms (Target, Walmart, etc.)
- [ ] Selenium integration for dynamic content
- [ ] Proxy rotation for better reliability
- [ ] Review sentiment analysis
- [ ] Temporal pattern detection
- [ ] Reviewer profile analysis
- [ ] API integration options

## API Reference

### ReviewScraper Class

```python
scraper = ReviewScraper(max_reviews=50, delay=1.5)

# Identify platform
platform = scraper.identify_platform(url)

# Scrape reviews
reviews = scraper.scrape_reviews(url)

# Convert to DataFrame
df = scraper.reviews_to_dataframe(reviews)
```

### Convenience Function

```python
from src.web_scraper import scrape_product_reviews

df = scrape_product_reviews(url, max_reviews=50)
```

## Support

For issues or questions:
1. Check the Streamlit app's error messages
2. Review this documentation
3. Consult the source code in `src/web_scraper.py`
4. Try the Batch Prediction feature as an alternative

## Version History

- **v1.1** (Current): URL Analysis feature added
- **v1.0**: Initial release with single and batch prediction

---

**Made with ❤️ | Fake Review Detector**
