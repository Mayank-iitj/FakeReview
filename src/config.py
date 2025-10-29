"""
Configuration file for the Fake Review Detector project.
Contains all configurable parameters and settings.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directory paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
VISUALIZATION_DIR = PROJECT_ROOT / "visualizations"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
VISUALIZATION_DIR.mkdir(exist_ok=True)

# Data file paths
RAW_DATA_PATH = DATA_DIR / "reviews.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_reviews.csv"

# Model file paths
BEST_MODEL_PATH = MODELS_DIR / "best_model.pkl"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"

# Data preprocessing settings
TEXT_COLUMN = "review_text"
LABEL_COLUMN = "label"
RATING_COLUMN = "rating"

# Class labels
FAKE_LABEL = "CG"  # Computer Generated
GENUINE_LABEL = "OR"  # Original Review

# Preprocessing parameters
REMOVE_STOPWORDS = True
APPLY_STEMMING = False  # Set to True if you want stemming
APPLY_LEMMATIZATION = True
MIN_WORD_LENGTH = 2

# Feature extraction settings
FEATURE_EXTRACTION_METHOD = "tfidf"  # Options: 'tfidf', 'countvectorizer'
MAX_FEATURES = 5000
MIN_DF = 2  # Minimum document frequency
MAX_DF = 0.8  # Maximum document frequency (proportion)
NGRAM_RANGE = (1, 2)  # Unigrams and bigrams

# Search settings
# Set to True to enable a broader, slower hyperparameter search for higher accuracy
EXPANDED_SEARCH = False

# Model training settings
TEST_SIZE = 0.2
RANDOM_STATE = 42
CROSS_VALIDATION_FOLDS = 5

# Models to train
MODELS_TO_TRAIN = [
    'naive_bayes',
    'random_forest',
    'svm',
    'logistic_regression',
    'decision_tree',
    'knn'
]

# Hyperparameter grids for tuning
HYPERPARAMETER_GRIDS = {
    'naive_bayes': {
        'alpha': [0.1, 0.5, 1.0, 2.0]
    },
    'random_forest': {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    },
    'svm': {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    },
    'logistic_regression': {
        'C': [0.1, 1, 10],
        'penalty': ['l2'],
        'solver': ['lbfgs', 'liblinear'],
        'max_iter': [200]
    },
    'decision_tree': {
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    },
    'knn': {
        'n_neighbors': [3, 5, 7, 9],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan']
    }
}

# Expanded hyperparameter grids for more exhaustive search
# Enable by setting EXPANDED_SEARCH=True
HYPERPARAMETER_GRIDS_EXPANDED = {
    'naive_bayes': {
        'alpha': [0.01, 0.1, 0.5, 1.0, 2.0]
    },
    'random_forest': {
        'n_estimators': [200, 400, 800],
        'max_depth': [None, 10, 20, 40],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    },
    'svm': {
        'C': [0.01, 0.1, 1, 10, 100],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    },
    'logistic_regression': {
        'C': [0.01, 0.1, 1, 10, 100],
        'penalty': ['l2'],
        'solver': ['lbfgs', 'liblinear'],
        'max_iter': [500]
    },
    'decision_tree': {
        'max_depth': [None, 10, 20, 40],
        'min_samples_split': [2, 5, 10, 20],
        'min_samples_leaf': [1, 2, 4]
    },
    'knn': {
        'n_neighbors': [3, 5, 7, 9, 11, 15],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan']
    }
}

# Visualization settings
FIGURE_SIZE = (10, 6)
DPI = 100
PLOT_STYLE = 'seaborn-v0_8-darkgrid'

# Application settings
APP_TITLE = "Fake Review Detector"
APP_DESCRIPTION = "Detect fake product reviews using machine learning"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
