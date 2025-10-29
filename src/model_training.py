"""
Model Training Module
Implements multiple machine learning classifiers with hyperparameter tuning.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Dict, Tuple, Any
import joblib
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    A class for training and evaluating multiple machine learning models.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the ModelTrainer.
        
        Args:
            random_state: Random state for reproducibility
        """
        self.random_state = random_state
        self.models = {}
        self.trained_models = {}
        self.best_model = None
        self.best_model_name = None
        self.best_score = 0.0
        self.label_encoder = LabelEncoder()
        
        # Initialize models
        self._initialize_models()
        
        logger.info("ModelTrainer initialized successfully")
    
    def _initialize_models(self):
        """Initialize all classification models."""
        self.models = {
            'naive_bayes': MultinomialNB(),
            'random_forest': RandomForestClassifier(random_state=self.random_state, n_jobs=-1),
            'svm': SVC(random_state=self.random_state, probability=True),
            'logistic_regression': LogisticRegression(random_state=self.random_state, max_iter=200, n_jobs=-1),
            'decision_tree': DecisionTreeClassifier(random_state=self.random_state),
            'knn': KNeighborsClassifier(n_jobs=-1)
        }
    
    def get_hyperparameter_grids(self) -> Dict[str, Dict]:
        """
        Get hyperparameter grids for all models.
        
        Returns:
            Dictionary of hyperparameter grids
        """
        # Prefer grids from config when available to centralize tuning
        try:
            try:
                from . import config as cfg  # when used as package
            except Exception:
                import config as cfg  # direct module import as last resort

            if getattr(cfg, 'EXPANDED_SEARCH', False) and hasattr(cfg, 'HYPERPARAMETER_GRIDS_EXPANDED'):
                return cfg.HYPERPARAMETER_GRIDS_EXPANDED
            if hasattr(cfg, 'HYPERPARAMETER_GRIDS'):
                return cfg.HYPERPARAMETER_GRIDS
        except Exception:
            pass

        # Fallback to built-in defaults
        return {
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
                'solver': ['lbfgs', 'liblinear']
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
    
    def encode_labels(self, y: pd.Series) -> np.ndarray:
        """
        Encode string labels to numerical values.
        
        Args:
            y: Series of labels
            
        Returns:
            Encoded labels as numpy array
        """
        return self.label_encoder.fit_transform(y)
    
    def decode_labels(self, y_encoded: np.ndarray) -> np.ndarray:
        """
        Decode numerical labels back to strings.
        
        Args:
            y_encoded: Encoded labels
            
        Returns:
            Original string labels
        """
        return self.label_encoder.inverse_transform(y_encoded)
    
    def train_model(self, 
                   model_name: str,
                   X_train: np.ndarray,
                   y_train: np.ndarray,
                   hyperparameter_tuning: bool = True,
                   cv_folds: int = 5) -> Tuple[Any, Dict]:
        """
        Train a single model with optional hyperparameter tuning.
        
        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training labels
            hyperparameter_tuning: Whether to perform hyperparameter tuning
            cv_folds: Number of cross-validation folds
            
        Returns:
            Tuple of (trained model, training info)
        """
        logger.info(f"\nTraining {model_name}...")
        start_time = time.time()
        
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model = self.models[model_name]
        
        if hyperparameter_tuning:
            # Get hyperparameter grid
            param_grid = self.get_hyperparameter_grids().get(model_name, {})
            
            if param_grid:
                logger.info(f"Performing hyperparameter tuning for {model_name}...")
                
                # GridSearchCV for hyperparameter tuning
                grid_search = GridSearchCV(
                    estimator=model,
                    param_grid=param_grid,
                    cv=cv_folds,
                    scoring='accuracy',
                    n_jobs=-1,
                    verbose=0
                )
                
                grid_search.fit(X_train, y_train)
                
                # Get best model
                model = grid_search.best_estimator_
                best_params = grid_search.best_params_
                cv_score = grid_search.best_score_
                
                logger.info(f"Best parameters: {best_params}")
                logger.info(f"Cross-validation score: {cv_score:.4f}")
            else:
                # Train without tuning
                model.fit(X_train, y_train)
                cv_score = np.mean(cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='accuracy'))
                best_params = {}
        else:
            # Train without tuning
            model.fit(X_train, y_train)
            cv_score = np.mean(cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='accuracy'))
            best_params = {}
        
        training_time = time.time() - start_time
        
        # Store training info
        training_info = {
            'model_name': model_name,
            'best_params': best_params,
            'cv_score': cv_score,
            'training_time': training_time
        }
        
        logger.info(f"Training completed in {training_time:.2f} seconds")
        
        return model, training_info
    
    def train_all_models(self,
                        X_train: np.ndarray,
                        y_train: np.ndarray,
                        models_to_train: list = None,
                        hyperparameter_tuning: bool = True,
                        cv_folds: int = 5) -> Dict[str, Dict]:
        """
        Train all specified models.
        
        Args:
            X_train: Training features
            y_train: Training labels
            models_to_train: List of model names to train (None = all models)
            hyperparameter_tuning: Whether to perform hyperparameter tuning
            cv_folds: Number of cross-validation folds
            
        Returns:
            Dictionary of training results
        """
        if models_to_train is None:
            models_to_train = list(self.models.keys())
        
        results = {}
        
        for model_name in models_to_train:
            try:
                model, info = self.train_model(
                    model_name=model_name,
                    X_train=X_train,
                    y_train=y_train,
                    hyperparameter_tuning=hyperparameter_tuning,
                    cv_folds=cv_folds
                )
                
                self.trained_models[model_name] = model
                results[model_name] = info
                
                # Track best model
                if info['cv_score'] > self.best_score:
                    self.best_score = info['cv_score']
                    self.best_model = model
                    self.best_model_name = model_name
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                results[model_name] = {'error': str(e)}
        
        logger.info(f"\nBest model: {self.best_model_name} (CV Score: {self.best_score:.4f})")
        
        return results
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using a trained model.
        
        Args:
            model_name: Name of the model to use
            X: Feature matrix
            
        Returns:
            Predictions
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        return self.trained_models[model_name].predict(X)
    
    def predict_proba(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities using a trained model.
        
        Args:
            model_name: Name of the model to use
            X: Feature matrix
            
        Returns:
            Prediction probabilities
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.trained_models[model_name]
        
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(X)
        else:
            raise ValueError(f"Model {model_name} does not support predict_proba")
    
    def save_model(self, model_name: str, file_path: str):
        """
        Save a trained model to disk.
        
        Args:
            model_name: Name of the model to save
            file_path: Path to save the model
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        joblib.dump(self.trained_models[model_name], file_path)
        logger.info(f"Model {model_name} saved to {file_path}")
    
    def save_best_model(self, file_path: str):
        """
        Save the best performing model to disk.
        
        Args:
            file_path: Path to save the model
        """
        if self.best_model is None:
            raise ValueError("No model trained yet")
        
        joblib.dump(self.best_model, file_path)
        logger.info(f"Best model ({self.best_model_name}) saved to {file_path}")
    
    def load_model(self, model_name: str, file_path: str):
        """
        Load a trained model from disk.
        
        Args:
            model_name: Name to assign to the loaded model
            file_path: Path to load the model from
        """
        self.trained_models[model_name] = joblib.load(file_path)
        logger.info(f"Model loaded from {file_path} as {model_name}")
    
    def save_label_encoder(self, file_path: str):
        """
        Save the label encoder to disk.
        
        Args:
            file_path: Path to save the encoder
        """
        joblib.dump(self.label_encoder, file_path)
        logger.info(f"Label encoder saved to {file_path}")
    
    def load_label_encoder(self, file_path: str):
        """
        Load the label encoder from disk.
        
        Args:
            file_path: Path to load the encoder from
        """
        self.label_encoder = joblib.load(file_path)
        logger.info(f"Label encoder loaded from {file_path}")


def split_data(X: np.ndarray, 
               y: np.ndarray, 
               test_size: float = 0.2,
               random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into training and testing sets.
    
    Args:
        X: Feature matrix
        y: Labels
        test_size: Proportion of data for testing
        random_state: Random state for reproducibility
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_classification
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=100, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train models
    results = trainer.train_all_models(X_train, y_train, models_to_train=['naive_bayes', 'logistic_regression'])
    
    print("\nTraining Results:")
    for model_name, info in results.items():
        print(f"{model_name}: {info}")
