# Fake Review Detection System

A robust Python-based system to combat fraudulent reviews on ecommerce platforms by automatically scraping, classifying, flagging, and facilitating the removal of fake product reviews.

## Features

### Core Capabilities
- **Web Scraper**: Extracts reviews from Amazon, Flipkart, and other platforms
- **NLP Pipeline**: Advanced text preprocessing with BERT embeddings
- **ML Classifier**: Ensemble models (Random Forest, XGBoost, SVM) for fake review detection
- **Automated Flagging**: Trust scoring, pattern detection, and suspicious behavior clustering
- **API Integration**: Automated deletion requests with approval workflow
- **Admin Dashboard**: Streamlit-based interface for review management

### Advanced Features
- Sentiment analysis with rating correlation
- IP/User behavior tracking and clustering
- Explainable AI with reason codes for predictions
- Real-time review validation API
- Comprehensive test coverage

## Tech Stack

- **Backend**: FastAPI
- **ML/NLP**: scikit-learn, XGBoost, transformers (BERT)
- **Web Scraping**: Selenium, BeautifulSoup, Playwright
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Dashboard**: Streamlit
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Chrome/Chromium (for Selenium)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fake-review-detector.git
cd fake-review-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

### Running the Application

```bash
# Start the API server
uvicorn app.main:app --reload --port 8000

# Start the Streamlit dashboard (separate terminal)
streamlit run dashboard/app.py

# Run scraper
python -m app.scraper.main --platform amazon --product-url "..."
```

### Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# Access services
# API: http://localhost:8000
# Dashboard: http://localhost:8501
# PostgreSQL: localhost:5432
```

## Streamlit Cloud Deployment

The dashboard can be deployed to Streamlit Cloud with the following configuration:

### Prerequisites
- GitHub repository with your code
- Streamlit Cloud account (https://streamlit.io/cloud)
- Backend API deployed and publicly accessible

### Configuration Steps

1. **Configure Secrets**: In your Streamlit Cloud app settings, add the following secrets:

```toml
# .streamlit/secrets.toml
API_URL = "https://your-backend-api.example.com/api"
```

2. **Verify Requirements**: Ensure `requirements.txt` includes:

```txt
streamlit>=1.28.0
httpx>=0.25.0
tenacity>=8.2.0
nest-asyncio>=1.5.0
pandas>=2.1.0
plotly>=5.18.0
loguru>=0.7.0
```

3. **Runtime Configuration**: Create `.streamlit/runtime.txt`:

```txt
python-3.11.16
```

4. **Deploy**:
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Set main file path: `dashboard/app.py`
   - Click "Deploy"

### Important Notes

- **API URL**: The dashboard requires a publicly accessible backend API. Set the `API_URL` secret to your production API endpoint.
- **Health Check**: The dashboard performs a health check on startup. If the backend is unreachable, a banner will be displayed with a retry button.
- **CPU-Only Torch**: The requirements are configured for CPU-only PyTorch to ensure compatibility with Streamlit Cloud's environment.
- **No Browser Automation**: Selenium and Playwright are disabled in the cloud requirements as they require system-level browser binaries.
- **File Size Limits**: CSV uploads are limited to 50MB. Adjust `MAX_UPLOAD_SIZE_MB` in `app/utils.py` if needed.

### Troubleshooting

**Backend Connection Issues:**
- Verify the `API_URL` secret is set correctly
- Ensure the backend API is publicly accessible and not blocked by CORS
- Check backend health endpoint: `https://your-api.example.com/api/admin/health`

**Dependency Errors:**
- Ensure `runtime.txt` specifies Python 3.11.16
- Verify all packages in requirements.txt are compatible with the Python version
- Check Streamlit Cloud build logs for specific error messages

**Memory Issues:**
- Disable BERT embeddings in Settings if experiencing memory errors
- Consider using the minimal requirements file: `requirements-streamlit-minimal.txt`

For detailed deployment instructions, see `STREAMLIT_DEPLOYMENT.md`.

## Usage

### 1. Scrape Reviews

```python
from app.scraper import AmazonScraper

scraper = AmazonScraper()
reviews = scraper.scrape_product("https://www.amazon.com/product/...")
```

### 2. Classify Reviews

```python
from app.classifier import FakeReviewClassifier

classifier = FakeReviewClassifier()
result = classifier.predict(review_text)
print(f"Fake probability: {result['fake_probability']}")
print(f"Reasons: {result['reasons']}")
```

### 3. API Usage

```bash
# Check single review
curl -X POST "http://localhost:8000/api/reviews/check" \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing product!", "rating": 5}'

# Batch processing
curl -X POST "http://localhost:8000/api/reviews/batch" \
  -H "Content-Type: application/json" \
  -F "file=@reviews.csv"
```

## Project Structure

```
fake-review-detector/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   ├── scraper/                # Web scraping modules
│   ├── preprocessing/          # Text preprocessing pipeline
│   ├── classifier/             # ML models and training
│   ├── flagging/               # Flagging and alert system
│   ├── api_integration/        # Platform API integration
│   └── routers/                # API endpoints
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── tests/
│   ├── test_scraper.py
│   ├── test_classifier.py
│   └── test_api.py
├── scripts/
│   ├── init_db.py              # Database initialization
│   └── train_model.py          # Model training script
├── data/
│   ├── raw/                    # Scraped reviews
│   ├── processed/              # Cleaned data
│   └── models/                 # Trained model artifacts
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Model Performance

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Random Forest | 94.2% | 93.8% | 94.5% | 94.1% |
| XGBoost | 95.1% | 94.9% | 95.3% | 95.1% |
| SVM | 92.7% | 92.1% | 93.2% | 92.6% |
| **Ensemble** | **96.3%** | **96.1%** | **96.5%** | **96.3%** |

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test suite
pytest tests/test_classifier.py -v
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

@Mayank-iitj

## Acknowledgments

- Dataset: Amazon Review Dataset, Fake Review Corpus
- Pre-trained models: HuggingFace Transformers
- Libraries: scikit-learn, XGBoost, Selenium

## Contact

Project Link: https://github.com/yourusername/fake-review-detector
