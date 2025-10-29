"""API Usage and Integration Guide."""

# Fake Review Detection System - API Guide

## REST API Overview

The system exposes a comprehensive REST API built with FastAPI for review classification, batch processing, and administration.

### Base URL
```
http://localhost:8000/api
```

### Authentication
Currently open (development). For production, implement:
- JWT tokens
- API keys
- OAuth 2.0

## Endpoints

### Review Endpoints

#### 1. Check Single Review

**Endpoint**: `POST /reviews/check`

**Request**:
```json
{
  "text": "Amazing product! Highly recommend!",
  "rating": 5.0,
  "product_id": "B001234567",
  "product_name": "Product Name",
  "platform": "amazon",
  "metadata": {
    "user_id": "user123",
    "country": "US"
  }
}
```

**Response**:
```json
{
  "review_id": 1,
  "fake_probability": 0.12,
  "is_fake": false,
  "confidence": 0.76,
  "reasons": [
    "Review appears genuine"
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid request
- `500`: Server error

#### 2. Batch Check Reviews

**Endpoint**: `POST /reviews/batch`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/reviews/batch" \
  -F "file=@reviews.csv"
```

**CSV Format** (headers required):
```csv
text,rating,product_id,platform
"Great product",5.0,B001,"amazon"
"Amazing!!!",5.0,B002,"flipkart"
```

**Response**:
```json
{
  "total_reviews": 2,
  "fake_count": 1,
  "genuine_count": 1,
  "results": [
    {
      "index": 0,
      "fake_probability": 0.15,
      "is_fake": false,
      "confidence": 0.70
    },
    {
      "index": 1,
      "fake_probability": 0.89,
      "is_fake": true,
      "confidence": 0.78
    }
  ]
}
```

#### 3. List Reviews

**Endpoint**: `GET /reviews/list`

**Query Parameters**:
- `platform`: Filter by platform (amazon, flipkart)
- `status`: Filter by status (pending, genuine, fake, flagged, removed)
- `limit`: Maximum results (default: 100)

**Example**:
```bash
curl "http://localhost:8000/api/reviews/list?platform=amazon&status=fake&limit=10"
```

**Response**: Array of reviews with classification details

#### 4. Get Review Details

**Endpoint**: `GET /reviews/{review_id}`

**Example**:
```bash
curl "http://localhost:8000/api/reviews/1"
```

**Response**:
```json
{
  "id": 1,
  "platform": "amazon",
  "product_name": "Product Name",
  "review_text": "...",
  "rating": 5.0,
  "reviewer_name": "User123",
  "status": "genuine",
  "fake_probability": 0.12,
  "trust_score": 0.88,
  "scraped_at": "2024-01-15T10:30:00Z"
}
```

### Admin Endpoints

#### 1. Dashboard Statistics

**Endpoint**: `GET /admin/dashboard/stats`

**Response**:
```json
{
  "total_reviews": 1500,
  "fake_reviews": 180,
  "genuine_reviews": 1200,
  "flagged_reviews": 100,
  "removed_reviews": 20,
  "fake_percentage": 12.0,
  "pending_deletions": 5,
  "average_trust_score": 0.85
}
```

#### 2. Get Flagged Reviews

**Endpoint**: `GET /admin/flagged-reviews`

**Query Parameters**:
- `limit`: Maximum results (default: 50)

**Response**: Array of flagged reviews with flag details

#### 3. Flag Review Manually

**Endpoint**: `POST /admin/reviews/{review_id}/flag`

**Request**:
```json
{
  "reason": "Detected as spam",
  "flag_type": "manual"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Review 123 flagged"
}
```

#### 4. Override Classification

**Endpoint**: `POST /admin/reviews/{review_id}/override`

**Request**:
```json
{
  "new_status": "genuine"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Review reclassified to genuine"
}
```

#### 5. Request Review Deletion

**Endpoint**: `POST /admin/reviews/{review_id}/request-deletion`

**Response**:
```json
{
  "deletion_request_id": 42,
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 6. Get Deletion Requests

**Endpoint**: `GET /admin/deletion-requests`

**Query Parameters**:
- `status`: pending, approved, rejected, submitted, completed, failed
- `limit`: Maximum results (default: 50)

### Scraper Endpoints

#### 1. Scrape Amazon Reviews

**Endpoint**: `POST /scraper/scrape/amazon`

**Request**:
```json
{
  "product_url": "https://www.amazon.com/dp/B001234567",
  "max_reviews": 100
}
```

**Response**:
```json
{
  "platform": "amazon",
  "product_url": "https://...",
  "total_reviews": 45,
  "reviews": [
    {
      "review_id": "amazon_R123",
      "review_text": "...",
      "rating": 4.5,
      "reviewer_name": "User123",
      "verified_purchase": true
    }
  ]
}
```

#### 2. Scrape Flipkart Reviews

**Endpoint**: `POST /scraper/scrape/flipkart`

**Request**:
```json
{
  "product_url": "https://www.flipkart.com/product/B001234567",
  "max_reviews": 100
}
```

**Response**: Same format as Amazon

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

| Code | Meaning | Likely Cause |
|------|---------|--------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters or malformed JSON |
| 404 | Not Found | Review or resource doesn't exist |
| 422 | Validation Error | Invalid data types or constraints |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Database or service temporarily down |

## Rate Limiting

Currently not implemented. For production:
- Implement rate limiting per IP/API key
- Recommended: 100 requests/minute

## Pagination

For list endpoints:
```bash
# Get page 2, 10 items per page (future implementation)
curl "http://localhost:8000/api/reviews/list?skip=10&limit=10"
```

## Code Examples

### Python

```python
import requests

# Single review check
response = requests.post(
    'http://localhost:8000/api/reviews/check',
    json={
        'text': 'Amazing product!',
        'rating': 5.0,
        'product_name': 'Widget Pro'
    }
)
result = response.json()
print(f"Fake: {result['is_fake']}, Confidence: {result['confidence']}")

# Batch processing
with open('reviews.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/reviews/batch',
        files={'file': f}
    )
result = response.json()
print(f"Fake: {result['fake_count']}, Genuine: {result['genuine_count']}")
```

### JavaScript/Node.js

```javascript
// Single review check
const response = await fetch('http://localhost:8000/api/reviews/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Amazing product!',
    rating: 5.0,
    product_name: 'Widget Pro'
  })
});
const result = await response.json();
console.log(`Fake: ${result.is_fake}, Confidence: ${result.confidence}`);
```

### cURL

```bash
# Single review
curl -X POST http://localhost:8000/api/reviews/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing product!",
    "rating": 5,
    "product_name": "Widget Pro"
  }'

# Dashboard stats
curl http://localhost:8000/api/admin/dashboard/stats

# List flagged reviews
curl http://localhost:8000/api/admin/flagged-reviews?limit=5
```

## Webhook Integration (Future)

```python
# Register webhook for new fake review detections
POST /webhooks/register
{
  "url": "https://your-service.com/webhook",
  "events": ["review.flagged", "review.removed"]
}
```

## API Documentation

Interactive Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

For more details, visit the [README.md](README.md) or see deployment instructions in [DEPLOYMENT.md](DEPLOYMENT.md)
