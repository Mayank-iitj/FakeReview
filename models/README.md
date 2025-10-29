# Models Directory

This directory stores the trained machine learning models and related artifacts.

## Generated Files:

After running the training pipeline (`python main.py`), you'll find:

### Model Files:
- `best_model.pkl` - The best performing model (automatically selected)
- `naive_bayes_model.pkl` - Naive Bayes classifier
- `random_forest_model.pkl` - Random Forest classifier
- `svm_model.pkl` - Support Vector Machine
- `logistic_regression_model.pkl` - Logistic Regression
- `decision_tree_model.pkl` - Decision Tree classifier
- `knn_model.pkl` - k-Nearest Neighbors classifier

### Supporting Files:
- `vectorizer.pkl` - TF-IDF/CountVectorizer for text feature extraction
- `label_encoder.pkl` - Label encoder for class labels
- `training_results.json` - Comprehensive training results and metrics
- `model_comparison.csv` - Performance comparison of all models

## Usage:

### Loading a Model:

```python
from src.prediction import ReviewPredictor

predictor = ReviewPredictor()
predictor.load_model(
    'models/best_model.pkl',
    'models/vectorizer.pkl',
    'models/label_encoder.pkl'
)

result = predictor.predict_single("Your review text here")
print(result)
```

### Model Persistence:

Models are saved using joblib for efficient serialization and deserialization.

## Notes:

- Model files are excluded from git (see .gitignore)
- Always keep the vectorizer and label encoder with the model
- Models can be retrained by running `python main.py`
