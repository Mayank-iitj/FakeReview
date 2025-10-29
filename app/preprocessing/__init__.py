"""Text preprocessing pipeline for reviews."""
import re
import string
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import spacy
from loguru import logger

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None


class ReviewPreprocessor:
    """Preprocesses review text for ML models."""
    
    def __init__(self):
        """Initialize preprocessor with NLP tools."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Keep some sentiment words that might be spam indicators
        self.stop_words -= {'not', 'no', 'very', 'too', 'most', 'best', 'worst'}
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw review text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Handle emojis (keep them for sentiment analysis)
        # Convert common emoji patterns to text
        text = text.replace('❤️', ' love ')
        text = text.replace('👍', ' like ')
        text = text.replace('👎', ' dislike ')
        text = text.replace('😊', ' happy ')
        text = text.replace('😢', ' sad ')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Cleaned text
            
        Returns:
            List of tokens
        """
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def remove_punctuation(self, tokens: List[str]) -> List[str]:
        """
        Remove punctuation from tokens.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token not in string.punctuation]
    
    def get_sentiment(self, text: str) -> Dict[str, float]:
        """
        Get sentiment scores using TextBlob.
        
        Args:
            text: Review text
            
        Returns:
            Dictionary with polarity and subjectivity scores
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def extract_features(self, text: str, rating: float) -> Dict:
        """
        Extract features from review for ML models.
        
        Args:
            text: Review text
            rating: Review rating
            
        Returns:
            Dictionary of features
        """
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        
        # Text statistics
        features = {
            'text_length': len(text),
            'word_count': len(tokens),
            'avg_word_length': np.mean([len(word) for word in tokens]) if tokens else 0,
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'digit_count': sum(1 for c in text if c.isdigit()),
            'special_char_count': sum(1 for c in text if c in string.punctuation),
        }
        
        # Sentiment
        sentiment = self.get_sentiment(cleaned_text)
        features.update(sentiment)
        
        # Rating features
        features['rating'] = rating
        features['sentiment_rating_diff'] = abs(sentiment['polarity'] - (rating / 5.0))
        
        # Spam indicators
        features['has_url'] = int(bool(re.search(r'http|www', text)))
        features['has_email'] = int(bool(re.search(r'\S+@\S+', text)))
        features['repeated_chars'] = max([len(match.group()) for match in re.finditer(r'(.)\1{2,}', text)] or [0])
        features['all_caps_words'] = sum(1 for word in tokens if word.isupper() and len(word) > 1)
        
        # Vocabulary richness
        unique_words = set(tokens)
        features['unique_word_ratio'] = len(unique_words) / len(tokens) if tokens else 0
        
        # Common spam phrases
        spam_phrases = ['click here', 'buy now', 'limited time', 'free shipping', 
                       'best product', 'highly recommend', 'must buy']
        features['spam_phrase_count'] = sum(1 for phrase in spam_phrases if phrase in cleaned_text)
        
        return features
    
    def preprocess(self, text: str, full_pipeline: bool = True) -> str:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Raw review text
            full_pipeline: Whether to apply full pipeline (lemmatization, etc.)
            
        Returns:
            Preprocessed text
        """
        # Clean text
        text = self.clean_text(text)
        
        if not full_pipeline:
            return text
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove punctuation
        tokens = self.remove_punctuation(tokens)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        tokens = self.lemmatize(tokens)
        
        # Join back
        return ' '.join(tokens)
    
    def detect_duplicates(self, reviews_df: pd.DataFrame, 
                         similarity_threshold: float = 0.9) -> pd.DataFrame:
        """
        Detect duplicate or near-duplicate reviews.
        
        Args:
            reviews_df: DataFrame with review texts
            similarity_threshold: Cosine similarity threshold
            
        Returns:
            DataFrame with duplicate flags
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Preprocess all reviews
        reviews_df['preprocessed'] = reviews_df['review_text'].apply(
            lambda x: self.preprocess(x, full_pipeline=False)
        )
        
        # Calculate TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(reviews_df['preprocessed'])
        
        # Calculate similarities
        similarities = cosine_similarity(tfidf_matrix)
        
        # Find duplicates
        duplicates = []
        for i in range(len(similarities)):
            for j in range(i + 1, len(similarities)):
                if similarities[i][j] >= similarity_threshold:
                    duplicates.append((i, j, similarities[i][j]))
        
        # Mark duplicates
        duplicate_indices = set()
        for i, j, sim in duplicates:
            duplicate_indices.add(j)  # Keep first occurrence
        
        reviews_df['is_duplicate'] = reviews_df.index.isin(duplicate_indices)
        
        logger.info(f"Found {len(duplicate_indices)} duplicate reviews")
        
        return reviews_df
    
    def batch_preprocess(self, reviews_df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess a batch of reviews.
        
        Args:
            reviews_df: DataFrame with review data
            
        Returns:
            DataFrame with preprocessed data and features
        """
        logger.info(f"Preprocessing {len(reviews_df)} reviews...")
        
        # Clean text
        reviews_df['cleaned_text'] = reviews_df['review_text'].apply(self.clean_text)
        
        # Extract features
        features_list = []
        for idx, row in reviews_df.iterrows():
            features = self.extract_features(row['review_text'], row['rating'])
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)
        reviews_df = pd.concat([reviews_df, features_df], axis=1)
        
        # Detect duplicates
        reviews_df = self.detect_duplicates(reviews_df)
        
        logger.info("Preprocessing complete")
        
        return reviews_df
