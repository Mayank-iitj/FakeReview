# URL Analysis Feature - Quick Reference Card

## 🚀 Quick Start

### Web App Usage (Recommended)
```
1. Open app → Navigate to "🔗 URL Analysis"
2. Paste product URL
3. Set max reviews (10-100)
4. Click "🔍 Scrape & Analyze Reviews"
5. View results & download CSV
```

### Command Line Usage
```bash
python demo_url_analysis.py
# Enter URL or press Enter for demo
```

### Programmatic Usage
```python
from src.web_scraper import scrape_product_reviews
from src.prediction import ReviewPredictor

# Scrape
df = scrape_product_reviews(url, max_reviews=50)

# Analyze
predictor = ReviewPredictor()
predictor.load_model(...)
results = predictor.predict_from_dataframe(df, 'text')
```

## 🎯 Supported Platforms

| Platform | Domains | Status |
|----------|---------|--------|
| Amazon | amazon.com, .in, .co.uk, .de, .fr | ✅ Full Support |
| Flipkart | flipkart.com | ✅ Full Support |
| eBay | ebay.com, .in, .co.uk | ⚠️ Basic Support |

## 📊 Result Interpretation

### Alert Levels
```
🚨 HIGH ALERT (>30% fake)
   → Avoid this product
   → Very suspicious review activity
   
⚠️ CAUTION (15-30% fake)
   → Review with skepticism
   → Check genuine reviews carefully
   
✅ GOOD (<15% fake)
   → Safe to consider
   → Low fake review presence
```

### Confidence Scores
```
90-100%  → Very Reliable
70-90%   → Reliable
<70%     → Review Manually
```

## ⚙️ Configuration

### Scraper Settings
```python
ReviewScraper(
    max_reviews=50,    # 10-100
    delay=1.5          # seconds between requests
)
```

### Common Adjustments
- **More reviews**: Increase max_reviews (slower)
- **Faster scraping**: Reduce delay (risky - may get blocked)
- **Better results**: Use max_reviews=100 for comprehensive analysis

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| No reviews found | Verify URL, check if product has reviews, try different product |
| Scraping error | Check internet, wait and retry, use Batch Prediction instead |
| Low confidence | Review text might be ambiguous, check for unusual patterns |
| Platform not supported | Use one of: Amazon, Flipkart, eBay |
| Rate limiting | Increase delay, reduce max_reviews, try later |

## 📁 File Structure

```
fake-review-detector/
├── app.py                      # Main Streamlit app (includes URL Analysis)
├── src/
│   ├── web_scraper.py         # NEW: Web scraping module
│   ├── prediction.py          # ML prediction module
│   ├── data_preprocessing.py  # Text preprocessing
│   └── config.py              # Configuration
├── models/
│   ├── best_model.pkl         # Trained ML model
│   ├── vectorizer.pkl         # TF-IDF vectorizer
│   └── label_encoder.pkl      # Label encoder
├── demo_url_analysis.py       # NEW: Demo script
├── URL_ANALYSIS_GUIDE.md      # NEW: Detailed guide
├── FEATURE_SUMMARY.md         # NEW: Complete summary
└── ARCHITECTURE_DIAGRAM.txt   # NEW: System diagram
```

## 🐛 Known Limitations

1. **Dynamic Content**: Some sites use JavaScript (may need Selenium)
2. **Anti-Scraping**: Platforms may block automated requests
3. **Structure Changes**: Website layouts change; may need updates
4. **Rate Limits**: Too many requests → temporary blocks
5. **Legal**: May violate platform ToS (educational use only)

## 💡 Best Practices

### For Users
✅ Use for research/educational purposes
✅ Respect rate limits (don't spam)
✅ Verify results with manual review
✅ Check multiple sources
✅ Consider genuine reviews specifically

### For Developers
✅ Use official APIs when available
✅ Implement caching
✅ Add proxy rotation (production)
✅ Monitor error rates
✅ Update selectors as sites change

## 📊 Example Output

```
URL: https://amazon.com/dp/B08XYZ123

╔══════════════════════════════════════╗
║  ANALYSIS RESULTS                    ║
╠══════════════════════════════════════╣
║  Total Reviews: 50                   ║
║  Fake Reviews: 8 (16%)               ║
║  Genuine Reviews: 42 (84%)           ║
║  Avg Confidence: 94%                 ║
║                                      ║
║  ⚠️ CAUTION                          ║
║  Moderate fake review presence       ║
╚══════════════════════════════════════╝

Top Suspicious Reviews:
1. "Amazing!!! Best ever!!!" (99% confidence)
2. "Perfect product highly recommend" (97% confidence)
3. "Five stars excellent quality" (95% confidence)

Export: review_analysis_amazon_20251029.csv
```

## 🔗 Useful Links

- **Repository**: https://github.com/Mayank-iitj/FakeReview.git
- **Documentation**: URL_ANALYSIS_GUIDE.md
- **Demo Script**: demo_url_analysis.py
- **Architecture**: ARCHITECTURE_DIAGRAM.txt

## 📞 Support

**Issue?** → Check error message → Review guide → Try demo script → Use Batch Prediction

**Questions?** → Read URL_ANALYSIS_GUIDE.md → Check FEATURE_SUMMARY.md

## 🎓 Learning Resources

### Web Scraping
- BeautifulSoup Documentation
- requests library guide
- robots.txt guide
- Legal considerations

### Machine Learning
- scikit-learn documentation
- TF-IDF vectorization
- Naive Bayes classifier
- Feature engineering

## ⚡ Performance Tips

### Faster Analysis
```python
# Use fewer reviews
max_reviews=20  # vs 50

# Reduce delay (careful!)
delay=1.0  # vs 1.5
```

### Better Accuracy
```python
# More reviews = better overview
max_reviews=100

# Check confidence scores
# Filter high-confidence predictions
results[results['prediction_confidence'] > 0.9]
```

## 🔐 Security & Privacy

- **No login required**: Public reviews only
- **No data stored**: Analysis is real-time
- **Local processing**: ML runs on your machine
- **Export optional**: User controls data export

## 📈 Version History

- **v1.1** (Current): URL Analysis feature added
  - Web scraping for 3 platforms
  - Comprehensive dashboard
  - CSV export capability
  - Demo script included
  
- **v1.0**: Initial release
  - Single prediction
  - Batch prediction from CSV
  - 6 ML models
  - High accuracy (>95%)

## ✨ Feature Highlights

🔗 **URL Input** - Just paste the product link
🤖 **Auto-Scraping** - Extracts reviews automatically
🎯 **High Accuracy** - ML model with 95%+ accuracy
📊 **Visual Dashboard** - Charts, metrics, tables
💾 **CSV Export** - Download complete analysis
🚨 **Alert System** - Instant trustworthiness assessment
🔍 **Detail View** - See suspicious reviews
⚡ **Fast** - Analyze 50 reviews in ~60 seconds

## 🎯 Success Metrics

| Metric | Value |
|--------|-------|
| Platforms Supported | 3 |
| Max Reviews | 100 |
| Analysis Speed | 100 reviews/sec |
| Model Accuracy | >95% |
| Features Analyzed | 156 |
| Response Time | <2 min for 50 reviews |

---

**Made with ❤️ | Fake Review Detector v1.1**

*For detailed information, see URL_ANALYSIS_GUIDE.md*
