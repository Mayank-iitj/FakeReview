"""Fake review classifier with ensemble ML models."""
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
from transformers import AutoTokenizer, AutoModel
import torch
from loguru import logger

from app.config import settings
from app.preprocessing import ReviewPreprocessor


class FakeReviewClassifier:
    """Ensemble classifier for fake review detection."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to saved model directory
        """
        self.model_path = Path(model_path or settings.MODEL_PATH)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.preprocessor = ReviewPreprocessor()
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
        
        # Initialize models
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        
        self.svm_model = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        
        # Ensemble weights (RF, XGBoost, SVM)
        self.ensemble_weights = settings.ensemble_weights_list
        
        # BERT model for embeddings (optional, can be resource-intensive)
        self.use_bert = False
        self.bert_tokenizer = None
        self.bert_model = None
        
    def enable_bert(self):
        """Enable BERT embeddings for enhanced feature extraction."""
        try:
            logger.info(f"Loading BERT model: {settings.NLP_MODEL}")
            self.bert_tokenizer = AutoTokenizer.from_pretrained(settings.NLP_MODEL)
            self.bert_model = AutoModel.from_pretrained(settings.NLP_MODEL)
            self.bert_model.eval()
            self.use_bert = True
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            self.use_bert = False
    
    def get_bert_embedding(self, text: str) -> np.ndarray:
        """
        Get BERT embedding for text.
        
        Args:
            text: Review text
            
        Returns:
            BERT embedding vector
        """
        if not self.use_bert:
            return np.array([])
        
        try:
            # Tokenize
            inputs = self.bert_tokenizer(
                text,
                return_tensors='pt',
                max_length=settings.NLP_MAX_LENGTH,
                truncation=True,
                padding=True
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].numpy().flatten()
            
            return embedding
        except Exception as e:
            logger.warning(f"Error getting BERT embedding: {e}")
            return np.array([])
    
    def extract_features(self, reviews_df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Extract features from reviews for classification.
        
        Args:
            reviews_df: DataFrame with review data
            
        Returns:
            Feature matrix and metadata DataFrame
        """
        logger.info("Extracting features...")
        
        # Preprocess reviews
        reviews_df = self.preprocessor.batch_preprocess(reviews_df)
        
        # TF-IDF features
        tfidf_features = self.vectorizer.fit_transform(
            reviews_df['cleaned_text']
        ).toarray()
        
        # Numerical features from preprocessing
        numerical_columns = [
            'text_length', 'word_count', 'avg_word_length', 'sentence_count',
            'exclamation_count', 'question_count', 'uppercase_ratio',
            'digit_count', 'special_char_count', 'polarity', 'subjectivity',
            'rating', 'sentiment_rating_diff', 'has_url', 'has_email',
            'repeated_chars', 'all_caps_words', 'unique_word_ratio',
            'spam_phrase_count'
        ]
        
        numerical_features = reviews_df[numerical_columns].fillna(0).values
        
        # Combine features
        features = np.hstack([tfidf_features, numerical_features])
        
        # Add BERT embeddings if enabled
        if self.use_bert:
            logger.info("Adding BERT embeddings...")
            bert_embeddings = []
            for text in reviews_df['review_text']:
                embedding = self.get_bert_embedding(text)
                bert_embeddings.append(embedding)
            
            bert_features = np.array(bert_embeddings)
            features = np.hstack([features, bert_features])
        
        logger.info(f"Feature extraction complete. Shape: {features.shape}")
        
        return features, reviews_df
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Train ensemble models.
        
        Args:
            X: Feature matrix
            y: Labels (0=genuine, 1=fake)
            
        Returns:
            Dictionary with training metrics
        """
        logger.info("Training ensemble models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        metrics = {}
        
        # Train Random Forest
        logger.info("Training Random Forest...")
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)
        rf_proba = self.rf_model.predict_proba(X_test)[:, 1]
        metrics['random_forest'] = self._calculate_metrics(y_test, rf_pred, rf_proba)
        
        # Train XGBoost
        logger.info("Training XGBoost...")
        self.xgb_model.fit(X_train, y_train)
        xgb_pred = self.xgb_model.predict(X_test)
        xgb_proba = self.xgb_model.predict_proba(X_test)[:, 1]
        metrics['xgboost'] = self._calculate_metrics(y_test, xgb_pred, xgb_proba)
        
        # Train SVM
        logger.info("Training SVM...")
        self.svm_model.fit(X_train, y_train)
        svm_pred = self.svm_model.predict(X_test)
        svm_proba = self.svm_model.predict_proba(X_test)[:, 1]
        metrics['svm'] = self._calculate_metrics(y_test, svm_pred, svm_proba)
        
        # Ensemble predictions
        ensemble_proba = (
            self.ensemble_weights[0] * rf_proba +
            self.ensemble_weights[1] * xgb_proba +
            self.ensemble_weights[2] * svm_proba
        )
        ensemble_pred = (ensemble_proba >= settings.PREDICTION_THRESHOLD).astype(int)
        metrics['ensemble'] = self._calculate_metrics(y_test, ensemble_pred, ensemble_proba)
        
        logger.info("Training complete!")
        logger.info(f"Ensemble Accuracy: {metrics['ensemble']['accuracy']:.4f}")
        logger.info(f"Ensemble F1-Score: {metrics['ensemble']['f1_score']:.4f}")
        
        return metrics
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                          y_proba: np.ndarray) -> Dict:
        """
        Calculate classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_proba)
        }
    
    def predict(self, review_text: str, rating: float, 
                metadata: Optional[Dict] = None) -> Dict:
        """
        Predict if a review is fake.
        
        Args:
            review_text: Review text
            rating: Review rating
            metadata: Optional metadata dictionary
            
        Returns:
            Prediction dictionary with probability and reasons
        """
        # Create DataFrame for single review
        review_df = pd.DataFrame([{
            'review_text': review_text,
            'rating': rating
        }])
        
        # Extract features
        features, processed_df = self.extract_features(review_df)
        
        # Get predictions from each model
        rf_proba = self.rf_model.predict_proba(features)[0, 1]
        xgb_proba = self.xgb_model.predict_proba(features)[0, 1]
        svm_proba = self.svm_model.predict_proba(features)[0, 1]
        
        # Ensemble probability
        fake_probability = (
            self.ensemble_weights[0] * rf_proba +
            self.ensemble_weights[1] * xgb_proba +
            self.ensemble_weights[2] * svm_proba
        )
        
        # Generate explanation
        reasons = self._generate_explanation(processed_df.iloc[0], fake_probability)
        
        return {
            'fake_probability': float(fake_probability),
            'is_fake': fake_probability >= settings.PREDICTION_THRESHOLD,
            'confidence': float(abs(fake_probability - 0.5) * 2),  # 0-1 scale
            'model_probabilities': {
                'random_forest': float(rf_proba),
                'xgboost': float(xgb_proba),
                'svm': float(svm_proba)
            },
            'reasons': reasons
        }
    
    def _generate_explanation(self, review_features: pd.Series, 
                             fake_probability: float) -> List[str]:
        """
        Generate human-readable explanation for classification.
        
        Args:
            review_features: Processed review features
            fake_probability: Fake probability score
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        if fake_probability < 0.3:
            reasons.append("Review appears genuine")
            return reasons
        
        # Check various indicators
        if review_features.get('spam_phrase_count', 0) > 2:
            reasons.append("Contains multiple spam phrases")
        
        if review_features.get('sentiment_rating_diff', 0) > 0.5:
            reasons.append("Sentiment doesn't match rating")
        
        if review_features.get('unique_word_ratio', 1) < 0.5:
            reasons.append("Low vocabulary diversity (repetitive text)")
        
        if review_features.get('uppercase_ratio', 0) > 0.3:
            reasons.append("Excessive use of capital letters")
        
        if review_features.get('exclamation_count', 0) > 5:
            reasons.append("Excessive use of exclamation marks")
        
        if review_features.get('word_count', 0) < 10:
            reasons.append("Review is suspiciously short")
        
        if review_features.get('all_caps_words', 0) > 3:
            reasons.append("Multiple words in ALL CAPS")
        
        if review_features.get('has_url', 0) == 1:
            reasons.append("Contains URLs")
        
        if not reasons:
            reasons.append(f"Statistical pattern matches fake reviews (confidence: {fake_probability:.2%})")
        
        return reasons
    
    def save(self, version: Optional[str] = None):
        """
        Save trained models to disk.
        
        Args:
            version: Model version string
        """
        version = version or settings.MODEL_VERSION
        save_dir = self.model_path / version
        save_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving models to {save_dir}")
        
        joblib.dump(self.rf_model, save_dir / 'random_forest.joblib')
        joblib.dump(self.xgb_model, save_dir / 'xgboost.joblib')
        joblib.dump(self.svm_model, save_dir / 'svm.joblib')
        joblib.dump(self.vectorizer, save_dir / 'vectorizer.joblib')
        joblib.dump(self.ensemble_weights, save_dir / 'ensemble_weights.joblib')
        
        logger.info("Models saved successfully")
    
    def load(self, version: Optional[str] = None):
        """
        Load trained models from disk.
        
        Args:
            version: Model version string
        """
        version = version or settings.MODEL_VERSION
        load_dir = self.model_path / version
        
        logger.info(f"Loading models from {load_dir}")
        
        self.rf_model = joblib.load(load_dir / 'random_forest.joblib')
        self.xgb_model = joblib.load(load_dir / 'xgboost.joblib')
        self.svm_model = joblib.load(load_dir / 'svm.joblib')
        self.vectorizer = joblib.load(load_dir / 'vectorizer.joblib')
        self.ensemble_weights = joblib.load(load_dir / 'ensemble_weights.joblib')
        
        logger.info("Models loaded successfully")
