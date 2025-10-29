# Fake Review Detector - Setup and Usage Guide

## Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/fake-review-detector.git
cd fake-review-detector

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

### 2. Prepare Your Dataset

Place your dataset CSV file at `data/reviews.csv` with the following format:

```csv
review_text,rating,label
"Amazing product! Highly recommend!",5,CG
"It's okay, nothing special.",3,OR
```

**Note:** If you don't have a dataset, the system will create a sample one automatically.

### 3. Train the Models

```bash
python main.py
```

This will:
- Load and preprocess the data
- Extract features using TF-IDF
- Train multiple ML models (Naive Bayes, Random Forest, SVM, etc.)
- Evaluate and compare models
- Save the best model
- Generate visualization plots

**Expected output:** Training takes 5-15 minutes depending on dataset size and hardware.

### 4. Run the Web Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features Overview

### 🔮 Single Prediction
- Analyze individual reviews
- Get instant classification (Fake/Genuine)
- View confidence scores
- See probability distributions

### 📊 Batch Prediction
- Upload CSV files with multiple reviews
- Batch process hundreds/thousands of reviews
- Download results as CSV
- View distribution charts

### 📈 Model Information
- View model performance metrics
- Compare different algorithms
- Check accuracy, precision, recall, F1-score

## Project Structure Explained

```
fake-review-detector/
├── src/                          # Source code modules
│   ├── config.py                # Configuration settings
│   ├── data_preprocessing.py    # Text cleaning & preprocessing
│   ├── feature_extraction.py    # TF-IDF & feature engineering
│   ├── model_training.py        # ML model training
│   ├── evaluation.py            # Model evaluation & metrics
│   ├── prediction.py            # Prediction interface
│   └── utils.py                 # Helper functions
│
├── data/                        # Dataset storage
│   └── reviews.csv             # Your dataset (place here)
│
├── models/                      # Trained models
│   ├── best_model.pkl          # Best performing model
│   ├── vectorizer.pkl          # Feature vectorizer
│   └── label_encoder.pkl       # Label encoder
│
├── visualizations/             # Generated plots
│   ├── class_distribution.png
│   ├── confusion_matrices/
│   └── model_comparison.png
│
├── main.py                     # Training pipeline
├── app.py                      # Streamlit web app
└── requirements.txt            # Dependencies
```

## Configuration

Edit `src/config.py` to customize:

- **Data paths:** Change file locations
- **Preprocessing:** Toggle stopword removal, stemming, lemmatization
- **Features:** Adjust max features, n-gram ranges
- **Models:** Select which models to train
- **Hyperparameters:** Customize model parameters

Example:
```python
# In src/config.py
MAX_FEATURES = 5000  # Change to 10000 for more features
APPLY_STEMMING = True  # Enable stemming
MODELS_TO_TRAIN = ['random_forest', 'svm']  # Train only these models
```

## Using the Prediction API

### Single Prediction

```python
from src.prediction import ReviewPredictor

predictor = ReviewPredictor()
predictor.load_model(
    'models/best_model.pkl',
    'models/vectorizer.pkl',
    'models/label_encoder.pkl'
)

review = "This product is absolutely amazing! Best purchase ever!"
result = predictor.predict_single(review)

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Batch Prediction

```python
reviews = [
    "Great product, highly recommend!",
    "Not bad, does the job.",
    "Terrible quality, waste of money."
]

results = predictor.predict_batch(reviews)

for i, result in enumerate(results):
    print(f"Review {i+1}: {result['prediction']} ({result['confidence']:.2%})")
```

### CSV File Prediction

```python
results_df = predictor.predict_from_csv(
    'input_reviews.csv',
    'output_predictions.csv',
    text_column='review_text'
)

print(results_df[['review_text', 'predicted_label', 'prediction_confidence']].head())
```

## Troubleshooting

### Issue: Import errors

**Solution:** Make sure you're in the project root directory and have activated the virtual environment.

### Issue: NLTK data not found

**Solution:** Download NLTK data:
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

### Issue: Model file not found

**Solution:** Run `python main.py` first to train the models.

### Issue: Low model accuracy

**Solution:** 
- Ensure you have a balanced, properly labeled dataset
- Increase dataset size (minimum 1000+ samples recommended)
- Adjust hyperparameters in `src/config.py`
- Try different feature extraction methods

### Issue: Streamlit app won't start

**Solution:**
```bash
# Make sure streamlit is installed
pip install streamlit

# Try running with full path
python -m streamlit run app.py
```

## Advanced Usage

### Custom Dataset Format

If your dataset has different column names:

```python
# In main.py or your script
from src import config

config.TEXT_COLUMN = 'review'  # Your text column name
config.LABEL_COLUMN = 'is_fake'  # Your label column name
```

### Retraining with New Data

1. Add new data to `data/reviews.csv`
2. Run `python main.py` again
3. New models will be trained and saved

### Using Different Algorithms

Edit `src/config.py`:

```python
MODELS_TO_TRAIN = [
    'random_forest',  # Usually best for text classification
    'svm',           # Good for high-dimensional data
    'logistic_regression'  # Fast and interpretable
]
```

## Performance Tips

### For Large Datasets:

1. **Reduce features:**
   ```python
   MAX_FEATURES = 3000  # Instead of 5000
   ```

2. **Disable hyperparameter tuning for initial runs:**
   ```python
   # In main.py
   training_results = trainer.train_all_models(
       X_train, y_train,
       hyperparameter_tuning=False  # Set to False
   )
   ```

3. **Use fewer models:**
   ```python
   MODELS_TO_TRAIN = ['random_forest']  # Train only one model
   ```

### For Better Accuracy:

1. **Increase features:**
   ```python
   MAX_FEATURES = 10000
   NGRAM_RANGE = (1, 3)  # Include trigrams
   ```

2. **Enable all preprocessing:**
   ```python
   REMOVE_STOPWORDS = True
   APPLY_LEMMATIZATION = True
   ```

3. **More training data:** Aim for 10,000+ samples

## Citation & Credits

If you use this project in your research or application, please cite:

```
Fake Review Detector
A machine learning system for detecting fake product reviews
https://github.com/YOUR_USERNAME/fake-review-detector
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact: your.email@example.com

---

**Happy Fake Review Detecting! 🔍**
