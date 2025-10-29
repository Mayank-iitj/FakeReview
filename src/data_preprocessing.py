"""
Data Preprocessing Module
Handles all text preprocessing tasks including cleaning, normalization,
stopword removal, stemming, and lemmatization.
"""

import re
import string
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from typing import List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    A class for preprocessing text data for machine learning models.
    """
    
    def __init__(self, 
                 remove_stopwords: bool = True,
                 apply_stemming: bool = False,
                 apply_lemmatization: bool = True,
                 min_word_length: int = 2):
        """
        Initialize the TextPreprocessor.
        
        Args:
            remove_stopwords: Whether to remove stopwords
            apply_stemming: Whether to apply stemming
            apply_lemmatization: Whether to apply lemmatization
            min_word_length: Minimum length of words to keep
        """
        self.remove_stopwords = remove_stopwords
        self.apply_stemming = apply_stemming
        self.apply_lemmatization = apply_lemmatization
        self.min_word_length = min_word_length
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize NLTK tools
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        logger.info("TextPreprocessor initialized successfully")
    
    def _download_nltk_data(self):
        """Download required NLTK datasets."""
        required_data = ['stopwords', 'punkt', 'wordnet', 'averaged_perceptron_tagger']
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.download(data, quiet=True)
                except:
                    pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing special characters, digits, and extra whitespace.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove digits
        text = re.sub(r'\d+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text string
            
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback to simple split if NLTK tokenization fails
            tokens = text.split()
        
        return tokens
    
    def remove_stopwords_from_tokens(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of tokens without stopwords
        """
        return [token for token in tokens if token not in self.stop_words]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Apply stemming to tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of stemmed tokens
        """
        return [self.stemmer.stem(token) for token in tokens]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Apply lemmatization to tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def filter_short_tokens(self, tokens: List[str]) -> List[str]:
        """
        Remove tokens shorter than minimum length.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of filtered tokens
        """
        return [token for token in tokens if len(token) >= self.min_word_length]
    
    def preprocess_text(self, text: str) -> str:
        """
        Apply all preprocessing steps to text.
        
        Args:
            text: Input text string
            
        Returns:
            Preprocessed text string
        """
        # Clean text
        text = self.clean_text(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords
        if self.remove_stopwords:
            tokens = self.remove_stopwords_from_tokens(tokens)
        
        # Filter short tokens
        tokens = self.filter_short_tokens(tokens)
        
        # Apply stemming
        if self.apply_stemming:
            tokens = self.stem_tokens(tokens)
        
        # Apply lemmatization
        if self.apply_lemmatization:
            tokens = self.lemmatize_tokens(tokens)
        
        # Join tokens back into text
        return ' '.join(tokens)
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Preprocess text column in a DataFrame.
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column to preprocess
            
        Returns:
            DataFrame with preprocessed text
        """
        logger.info(f"Preprocessing {len(df)} reviews...")
        
        # Create a copy to avoid modifying original
        df_processed = df.copy()
        
        # Apply preprocessing
        df_processed['processed_text'] = df_processed[text_column].apply(
            lambda x: self.preprocess_text(x) if pd.notna(x) else ""
        )
        
        logger.info("Preprocessing completed successfully")
        
        return df_processed


def extract_text_features(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Extract additional features from text data.
    
    Args:
        df: Input DataFrame
        text_column: Name of the text column
        
    Returns:
        DataFrame with additional features
    """
    df_features = df.copy()
    
    # Text length (character count)
    df_features['text_length'] = df_features[text_column].apply(
        lambda x: len(str(x)) if pd.notna(x) else 0
    )
    
    # Word count
    df_features['word_count'] = df_features[text_column].apply(
        lambda x: len(str(x).split()) if pd.notna(x) else 0
    )
    
    # Average word length
    df_features['avg_word_length'] = df_features.apply(
        lambda row: row['text_length'] / row['word_count'] if row['word_count'] > 0 else 0,
        axis=1
    )
    
    # Count of uppercase letters (as proportion)
    df_features['uppercase_ratio'] = df_features[text_column].apply(
        lambda x: sum(1 for c in str(x) if c.isupper()) / len(str(x)) if len(str(x)) > 0 else 0
    )
    
    # Count of exclamation marks
    df_features['exclamation_count'] = df_features[text_column].apply(
        lambda x: str(x).count('!')
    )
    
    # Count of question marks
    df_features['question_count'] = df_features[text_column].apply(
        lambda x: str(x).count('?')
    )
    
    logger.info("Text features extracted successfully")
    
    return df_features


def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Handle missing values in the DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: Strategy to handle missing values ('drop' or 'fill')
        
    Returns:
        DataFrame with handled missing values
    """
    df_cleaned = df.copy()
    
    if strategy == 'drop':
        # Drop rows with missing values in critical columns
        initial_count = len(df_cleaned)
        df_cleaned = df_cleaned.dropna(subset=['review_text', 'label'])
        dropped_count = initial_count - len(df_cleaned)
        logger.info(f"Dropped {dropped_count} rows with missing values")
    
    elif strategy == 'fill':
        # Fill missing text with empty string
        df_cleaned['review_text'].fillna('', inplace=True)
        
        # Fill missing ratings with median
        if 'rating' in df_cleaned.columns:
            df_cleaned['rating'].fillna(df_cleaned['rating'].median(), inplace=True)
        
        logger.info("Missing values filled")
    
    return df_cleaned


def load_and_preprocess_data(file_path: str, 
                            text_column: str = 'review_text',
                            label_column: str = 'label',
                            remove_stopwords: bool = True,
                            apply_stemming: bool = False,
                            apply_lemmatization: bool = True) -> pd.DataFrame:
    """
    Load and preprocess data from CSV file.
    
    Args:
        file_path: Path to CSV file
        text_column: Name of text column
        label_column: Name of label column
        remove_stopwords: Whether to remove stopwords
        apply_stemming: Whether to apply stemming
        apply_lemmatization: Whether to apply lemmatization
        
    Returns:
        Preprocessed DataFrame
    """
    logger.info(f"Loading data from {file_path}...")
    
    # Load data
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} reviews")
    
    # Handle missing values
    df = handle_missing_values(df, strategy='drop')
    
    # Extract text features before preprocessing
    df = extract_text_features(df, text_column)
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        remove_stopwords=remove_stopwords,
        apply_stemming=apply_stemming,
        apply_lemmatization=apply_lemmatization
    )
    
    # Preprocess text
    df = preprocessor.preprocess_dataframe(df, text_column)
    
    logger.info("Data preprocessing pipeline completed successfully")
    
    return df


if __name__ == "__main__":
    # Example usage
    sample_text = "This is an AMAZING product!!! I highly recommend it. Best purchase ever!"
    
    preprocessor = TextPreprocessor()
    processed = preprocessor.preprocess_text(sample_text)
    
    print(f"Original: {sample_text}")
    print(f"Processed: {processed}")
