"""
Feature Extraction Module
Implements TF-IDF and Count Vectorization for converting text to numerical features.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from typing import Tuple, Optional
import joblib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    A class for extracting features from text data using various vectorization methods.
    """
    
    def __init__(self, 
                 method: str = 'tfidf',
                 max_features: int = 5000,
                 ngram_range: Tuple[int, int] = (1, 2),
                 min_df: int = 2,
                 max_df: float = 0.8):
        """
        Initialize the FeatureExtractor.
        
        Args:
            method: Vectorization method ('tfidf' or 'countvectorizer')
            max_features: Maximum number of features to extract
            ngram_range: The n-gram range to use
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        self.method = method
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer = None
        
        # Initialize vectorizer based on method
        self._initialize_vectorizer()
        
        logger.info(f"FeatureExtractor initialized with {method} method")
    
    def _initialize_vectorizer(self):
        """Initialize the appropriate vectorizer based on the method."""
        if self.method == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df,
                strip_accents='unicode',
                lowercase=True,
                analyzer='word',
                token_pattern=r'\w{2,}',  # Words with at least 2 characters
                stop_words=None  # We already removed stopwords in preprocessing
            )
        elif self.method == 'countvectorizer':
            self.vectorizer = CountVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df,
                strip_accents='unicode',
                lowercase=True,
                analyzer='word',
                token_pattern=r'\w{2,}',
                stop_words=None
            )
        else:
            raise ValueError(f"Unknown method: {self.method}. Use 'tfidf' or 'countvectorizer'")
    
    def fit_transform(self, texts: pd.Series) -> np.ndarray:
        """
        Fit the vectorizer on texts and transform them to feature vectors.
        
        Args:
            texts: Series of text data
            
        Returns:
            Feature matrix as numpy array
        """
        logger.info(f"Fitting {self.method} vectorizer on {len(texts)} documents...")
        
        # Fit and transform
        features = self.vectorizer.fit_transform(texts)
        
        logger.info(f"Extracted {features.shape[1]} features from text")
        
        return features.toarray()
    
    def transform(self, texts: pd.Series) -> np.ndarray:
        """
        Transform texts to feature vectors using fitted vectorizer.
        
        Args:
            texts: Series of text data
            
        Returns:
            Feature matrix as numpy array
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Call fit_transform first.")
        
        logger.info(f"Transforming {len(texts)} documents...")
        
        features = self.vectorizer.transform(texts)
        
        return features.toarray()
    
    def get_feature_names(self) -> list:
        """
        Get the feature names from the vectorizer.
        
        Returns:
            List of feature names
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted.")
        
        try:
            # For newer scikit-learn versions
            return self.vectorizer.get_feature_names_out().tolist()
        except AttributeError:
            # For older scikit-learn versions
            return self.vectorizer.get_feature_names()
    
    def get_top_features(self, n: int = 20) -> list:
        """
        Get the top n most important features.
        
        Args:
            n: Number of top features to return
            
        Returns:
            List of top feature names
        """
        feature_names = self.get_feature_names()
        
        if self.method == 'tfidf':
            # Get average TF-IDF scores across all documents
            if hasattr(self.vectorizer, 'idf_'):
                idf_scores = self.vectorizer.idf_
                top_indices = np.argsort(idf_scores)[::-1][:n]
                return [feature_names[i] for i in top_indices]
        
        return feature_names[:n]
    
    def save_vectorizer(self, file_path: str):
        """
        Save the fitted vectorizer to disk.
        
        Args:
            file_path: Path to save the vectorizer
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Nothing to save.")
        
        joblib.dump(self.vectorizer, file_path)
        logger.info(f"Vectorizer saved to {file_path}")
    
    def load_vectorizer(self, file_path: str):
        """
        Load a fitted vectorizer from disk.
        
        Args:
            file_path: Path to load the vectorizer from
        """
        self.vectorizer = joblib.load(file_path)
        logger.info(f"Vectorizer loaded from {file_path}")


def combine_features(text_features: np.ndarray, 
                     additional_features: pd.DataFrame,
                     feature_columns: list) -> np.ndarray:
    """
    Combine text features with additional numerical features.
    
    Args:
        text_features: Text feature matrix from vectorization
        additional_features: DataFrame with additional features
        feature_columns: List of column names to include
        
    Returns:
        Combined feature matrix
    """
    # Extract additional features
    add_features = additional_features[feature_columns].values
    
    # Combine features
    combined = np.hstack([text_features, add_features])
    
    logger.info(f"Combined features shape: {combined.shape}")
    
    return combined


def extract_features(df: pd.DataFrame,
                    text_column: str = 'processed_text',
                    method: str = 'tfidf',
                    max_features: int = 5000,
                    ngram_range: Tuple[int, int] = (1, 2),
                    min_df: int = 2,
                    max_df: float = 0.8,
                    include_additional_features: bool = True) -> Tuple[np.ndarray, FeatureExtractor]:
    """
    Extract features from DataFrame.
    
    Args:
        df: Input DataFrame
        text_column: Name of the text column
        method: Vectorization method
        max_features: Maximum number of features
        include_additional_features: Whether to include additional features
        
    Returns:
        Tuple of (feature matrix, feature extractor)
    """
    # Initialize feature extractor
    extractor = FeatureExtractor(
        method=method,
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df
    )
    
    # Extract text features
    text_features = extractor.fit_transform(df[text_column])
    
    # Include additional features if requested
    if include_additional_features:
        additional_feature_columns = [
            'text_length', 'word_count', 'avg_word_length',
            'uppercase_ratio', 'exclamation_count', 'question_count'
        ]
        
        # Filter to only include columns that exist
        existing_columns = [col for col in additional_feature_columns if col in df.columns]
        
        if existing_columns:
            features = combine_features(text_features, df, existing_columns)
        else:
            features = text_features
    else:
        features = text_features
    
    logger.info(f"Final feature matrix shape: {features.shape}")
    
    return features, extractor


def analyze_feature_importance(extractor: FeatureExtractor, 
                              class_labels: np.ndarray,
                              n_top: int = 20):
    """
    Analyze and display top features for each class.
    
    Args:
        extractor: Fitted FeatureExtractor
        class_labels: Array of class labels
        n_top: Number of top features to display
    """
    feature_names = extractor.get_feature_names()
    
    if extractor.method == 'tfidf' and hasattr(extractor.vectorizer, 'idf_'):
        print(f"\nTop {n_top} features by IDF score:")
        print("-" * 50)
        
        idf_scores = extractor.vectorizer.idf_
        top_indices = np.argsort(idf_scores)[::-1][:n_top]
        
        for idx in top_indices:
            print(f"{feature_names[idx]}: {idf_scores[idx]:.4f}")


if __name__ == "__main__":
    # Example usage
    sample_texts = pd.Series([
        "great product highly recommend",
        "terrible quality waste money",
        "amazing experience best purchase",
        "poor service disappointed"
    ])
    
    extractor = FeatureExtractor(method='tfidf', max_features=100)
    features = extractor.fit_transform(sample_texts)
    
    print(f"Feature matrix shape: {features.shape}")
    print(f"Top features: {extractor.get_top_features(n=10)}")
