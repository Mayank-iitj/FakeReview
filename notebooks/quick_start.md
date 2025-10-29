# Quick Start Example

This notebook demonstrates how to use the Fake Review Detector.

## 1. Import Libraries

```python
import sys
sys.path.insert(0, '..')

from src.prediction import ReviewPredictor
from src.utils import create_sample_dataset
import pandas as pd
```

## 2. Create Sample Data (if needed)

```python
# Create a small sample dataset
create_sample_dataset('data/sample_reviews.csv', n_samples=100)
```

## 3. Train Models (First Time Only)

```python
# Run this in terminal instead:
# python main.py
```

## 4. Load Trained Model

```python
predictor = ReviewPredictor()
predictor.load_model(
    '../models/best_model.pkl',
    '../models/vectorizer.pkl',
    '../models/label_encoder.pkl'
)
```

## 5. Make Predictions

### Single Prediction

```python
review = "This product is absolutely amazing! Best purchase ever! Highly recommend!"
result = predictor.predict_single(review)

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Probabilities: {result['probabilities']}")
```

### Batch Prediction

```python
reviews = [
    "Great product, highly recommend!",
    "It's okay, does what it says.",
    "Terrible quality, complete waste of money."
]

results = predictor.predict_batch(reviews)

for i, result in enumerate(results):
    print(f"\nReview {i+1}:")
    print(f"  Text: {result['original_text']}")
    print(f"  Prediction: {result['prediction']}")
    print(f"  Confidence: {result['confidence']:.2%}")
```

### CSV Prediction

```python
# Predict from CSV file
results_df = predictor.predict_from_csv(
    'data/sample_reviews.csv',
    'data/predictions.csv',
    text_column='review_text'
)

print(results_df[['review_text', 'predicted_label', 'prediction_confidence']].head())
```

## 6. Analyze Results

```python
# Get summary statistics
summary = predictor.get_prediction_summary(results)
print("\nPrediction Summary:")
print(f"  Total: {summary['total_predictions']}")
print(f"  Distribution: {summary['prediction_distribution']}")
print(f"  Avg Confidence: {summary['average_confidence']:.2%}")
```

## 7. Visualize Results

```python
import matplotlib.pyplot as plt

# Plot prediction distribution
distribution = summary['prediction_distribution']
plt.figure(figsize=(8, 6))
plt.bar(distribution.keys(), distribution.values())
plt.title('Prediction Distribution')
plt.xlabel('Class')
plt.ylabel('Count')
plt.show()
```

## Next Steps

- Run the Streamlit app: `streamlit run app.py`
- Explore model performance in the visualizations folder
- Try your own reviews!
