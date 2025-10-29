"""Project structure information."""
# Project Structure

```
fake-review-detector/
│
├── app/                              # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   ├── config.py                     # Configuration management
│   ├── database.py                   # Database connection & session
│   ├── schemas.py                    # Pydantic request/response models
│   │
│   ├── models/
│   │   └── __init__.py              # SQLAlchemy ORM models
│   │       - Review, Flag, DeletionRequest, User, ReviewerProfile, IPCluster
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── reviews.py               # Review classification endpoints
│   │   ├── admin.py                 # Admin dashboard endpoints
│   │   └── scraper.py               # Web scraping endpoints
│   │
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base scraper with Selenium setup
│   │   ├── amazon.py                # Amazon scraper implementation
│   │   └── flipkart.py              # Flipkart scraper implementation
│   │
│   ├── preprocessing/
│   │   └── __init__.py              # ReviewPreprocessor class
│   │       - Text cleaning, tokenization, feature extraction
│   │
│   └── classifier/
│       └── __init__.py              # FakeReviewClassifier with ensemble models
│           - Random Forest, XGBoost, SVM, BERT embeddings
│
├── dashboard/
│   └── app.py                       # Streamlit admin dashboard
│
├── scripts/
│   ├── init_db.py                   # Database initialization
│   ├── train_model.py               # Model training script
│   └── generate_demo_data.py        # Generate sample reviews
│
├── tests/
│   └── test_system.py               # Unit and integration tests
│
├── data/
│   ├── raw/                         # Scraped raw reviews
│   ├── processed/                   # Preprocessed data
│   └── models/                      # Trained model artifacts
│
├── logs/
│   └── app.log                      # Application logs
│
├── docker/
│   ├── Dockerfile                   # Container image definition
│   └── docker-compose.yml           # Multi-service orchestration
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
├── README.md                        # Project documentation
├── DEPLOYMENT.md                    # Deployment guide
├── API_GUIDE.md                     # API reference
├── MODEL_EVALUATION.md              # Model performance report
├── setup.sh                         # Linux/Mac setup script
└── setup.bat                        # Windows setup script
```

## Key Directories

### `/app` - Application Core
- **main.py**: FastAPI application with middleware and error handling
- **models/**: SQLAlchemy ORM models for database tables
- **routers/**: API endpoint definitions organized by feature
- **scraper/**: Web scraping modules with anti-detection
- **preprocessing/**: NLP pipeline for text processing
- **classifier/**: ML ensemble models for classification

### `/dashboard` - Admin Interface
- Streamlit application for monitoring and management
- Real-time statistics and flagged review visualization
- Manual review checking interface
- Batch processing upload interface

### `/scripts` - Utilities
- Database initialization
- Model training with sample data
- Demo data generation
- Maintenance scripts (future)

### `/data` - Storage
- **raw/**: Original scraped reviews
- **processed/**: Cleaned and feature-engineered data
- **models/**: Serialized trained models

### `/tests` - Quality Assurance
- Unit tests for core modules
- Integration tests for API endpoints
- Sample data for testing

### `/docker` - Deployment
- **Dockerfile**: Container image with all dependencies
- **docker-compose.yml**: Services (API, Dashboard, PostgreSQL, Redis, Celery)

## Core Components

### 1. Review Scraper
- `app/scraper/amazon.py`: Amazon product reviews
- `app/scraper/flipkart.py`: Flipkart product reviews
- Anti-detection measures: rotating user agents, random delays, headless browser

### 2. Preprocessing Pipeline
- `app/preprocessing/__init__.py`: ReviewPreprocessor class
- Text cleaning, tokenization, lemmatization
- Feature extraction: statistical, sentiment, spam indicators
- Duplicate detection using TF-IDF similarity

### 3. ML Classifier
- `app/classifier/__init__.py`: FakeReviewClassifier
- Ensemble: Random Forest (40%), XGBoost (35%), SVM (25%)
- Features: TF-IDF + statistical features + optional BERT embeddings
- Prediction with explainability and confidence scores

### 4. API Layer
- **Reviews Router**: Single/batch classification, list, details
- **Admin Router**: Statistics, flagging, overrides, deletion requests
- **Scraper Router**: Trigger web scraping jobs

### 5. Dashboard
- **Streamlit App**: Real-time monitoring and interaction
- Pages: Dashboard, Flagged Reviews, Manual Check, Batch Analysis, Settings

## Database Schema

### Tables
1. **reviews**: Core review data with classification
2. **flags**: Suspicious flags attached to reviews
3. **deletion_requests**: Track removal workflow
4. **users**: Admin users with roles
5. **reviewer_profiles**: Behavior analytics per reviewer
6. **ip_clusters**: Spam IP detection

## API Endpoints

### Review Endpoints (`/api/reviews`)
- `POST /check`: Single review classification
- `POST /batch`: Batch CSV upload processing
- `GET /list`: Query reviews with filters
- `GET /{review_id}`: Get review details

### Admin Endpoints (`/api/admin`)
- `GET /dashboard/stats`: Dashboard metrics
- `GET /flagged-reviews`: List flagged reviews
- `POST /reviews/{id}/flag`: Manual flagging
- `POST /reviews/{id}/override`: Reclassify reviews
- `POST /reviews/{id}/request-deletion`: Request removal
- `GET /deletion-requests`: View deletion queue

### Scraper Endpoints (`/api/scraper`)
- `POST /scrape/amazon`: Scrape Amazon reviews
- `POST /scrape/flipkart`: Scrape Flipkart reviews

## Environment Variables

Key variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis cache connection
- `NLP_MODEL`: BERT model identifier
- `PREDICTION_THRESHOLD`: Classification threshold (0-1)
- `ENSEMBLE_WEIGHTS`: Model ensemble weights
- `SCRAPER_*`: Scraping configuration
- `JWT_SECRET_KEY`: Authentication secret
- Logging and email settings

## Technology Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy ORM
- **ML/NLP**: scikit-learn, XGBoost, transformers (BERT)
- **Web Scraping**: Selenium, BeautifulSoup, Playwright
- **Dashboard**: Streamlit, Plotly
- **Task Queue**: Celery, Redis
- **Testing**: pytest
- **Deployment**: Docker, Docker Compose
- **Logging**: Loguru

See [README.md](README.md) for detailed usage instructions.
