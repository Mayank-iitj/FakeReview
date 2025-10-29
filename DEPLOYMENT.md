"""Quick start guide for deployment."""

# Fake Review Detection System - Deployment Guide

## Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Docker & Docker Compose (optional)
- Chrome/Chromium (for Selenium web scraping)

## Local Development Setup

### 1. Clone and Setup

```bash
cd fake-review-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 2. Environment Configuration

```bash
# Copy and customize environment variables
cp .env.example .env

# Edit .env with your configuration:
# - Database credentials
# - API keys
# - Model paths
```

### 3. Database Setup

```bash
# Create database
createdb fake_review_db

# Initialize tables
python scripts/init_db.py

# Train initial models
python scripts/train_model.py

# Generate demo data
python scripts/generate_demo_data.py
```

### 4. Start Services

```bash
# Terminal 1: Start API server
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start dashboard
streamlit run dashboard/app.py --server.port 8501
```

Access the system at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

Services will be available at:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- PostgreSQL: localhost:5432

### Scaling on Cloud Platforms

#### AWS ECS/Fargate

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {account}.dkr.ecr.us-east-1.amazonaws.com
docker tag fake-review-detector:latest {account}.dkr.ecr.us-east-1.amazonaws.com/fake-review-detector:latest
docker push {account}.dkr.ecr.us-east-1.amazonaws.com/fake-review-detector:latest

# Deploy with CloudFormation or ECS console
```

#### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/{project}/fake-review-detector

# Deploy
gcloud run deploy fake-review-detector \
  --image gcr.io/{project}/fake-review-detector \
  --platform managed \
  --region us-central1
```

#### Heroku

```bash
# Login and create app
heroku login
heroku create fake-review-detector

# Add PostgreSQL add-on
heroku addons:create heroku-postgresql:standard-0

# Deploy
git push heroku main

# Open app
heroku open
```

## API Usage Examples

### Check Single Review

```bash
curl -X POST "http://localhost:8000/api/reviews/check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing product! Highly recommend!",
    "rating": 5,
    "product_name": "Widget Pro",
    "platform": "amazon"
  }'
```

### Batch Processing

```bash
# Create CSV file: reviews.csv
# Format: text, rating, product_id, platform

curl -X POST "http://localhost:8000/api/reviews/batch" \
  -F "file=@reviews.csv"
```

### Get Dashboard Stats

```bash
curl http://localhost:8000/api/admin/dashboard/stats
```

### List Flagged Reviews

```bash
curl "http://localhost:8000/api/admin/flagged-reviews?limit=20"
```

## Monitoring and Logs

### View Application Logs

```bash
# Local
tail -f logs/app.log

# Docker
docker-compose logs -f api

# Docker with grep
docker-compose logs api | grep ERROR
```

### Performance Metrics

The system tracks:
- API response times
- Model inference time
- Database query performance
- Scraper success rates

Access via Prometheus endpoint (if enabled):
http://localhost:9090

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -U postgres -d fake_review_db -c "SELECT 1"

# Check environment variables
echo $DATABASE_URL
```

### Selenium/Browser Issues

```bash
# Ensure Chrome is installed
google-chrome --version

# Update chromedriver
pip install --upgrade webdriver-manager
```

### Model Loading Issues

```bash
# Verify model files exist
ls -la data/models/v1.0/

# Check model format
file data/models/v1.0/random_forest.joblib
```

### Memory Issues

```bash
# Reduce batch size in .env
NLP_BATCH_SIZE=16

# Disable BERT embeddings if not needed
# Or reduce model size in preprocessing
```

## Performance Optimization

### Enable Caching

```python
# In app/config.py
REDIS_URL = "redis://localhost:6379/0"
```

### Database Indexing

```sql
-- Create indices for faster queries
CREATE INDEX idx_review_status ON reviews(status);
CREATE INDEX idx_review_platform ON reviews(platform);
CREATE INDEX idx_review_fake_prob ON reviews(fake_probability);
CREATE INDEX idx_flag_review_id ON flags(review_id);
```

### Model Optimization

```bash
# Convert models to ONNX for faster inference
python scripts/optimize_models.py
```

## Maintenance

### Regular Backups

```bash
# Backup PostgreSQL
pg_dump fake_review_db > backup_$(date +%Y%m%d).sql

# Restore
psql fake_review_db < backup_*.sql
```

### Model Retraining

```bash
# Monthly retraining with new data
python scripts/train_model.py --data data/processed/monthly_reviews.csv

# Evaluate performance
python scripts/evaluate_model.py
```

### Clean Old Data

```bash
# Archive reviews older than 90 days
python scripts/archive_old_reviews.py --days 90
```

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Contributing**: See CONTRIBUTING.md

## License

MIT License - See LICENSE file for details
