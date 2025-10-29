"""
Prediction Module
Handles single and batch predictions using trained models.
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, List, Union
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewPredictor:
    """
    A class for making predictions on product reviews.
    """
    
    def __init__(self):
        """Initialize the ReviewPredictor."""
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.preprocessor = None
        
        logger.info("ReviewPredictor initialized")
    
    def load_model(self, model_path: str, vectorizer_path: str = None, 
                   label_encoder_path: str = None):
        """
        Load trained model and associated components.
        
        Args:
            model_path: Path to the trained model file
            vectorizer_path: Path to the vectorizer file
            label_encoder_path: Path to the label encoder file
        """
        try:
            # Load model
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
            
            # Load vectorizer if path provided
            if vectorizer_path and Path(vectorizer_path).exists():
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info(f"Vectorizer loaded from {vectorizer_path}")
            
            # Load label encoder if path provided
            if label_encoder_path and Path(label_encoder_path).exists():
                self.label_encoder = joblib.load(label_encoder_path)
                logger.info(f"Label encoder loaded from {label_encoder_path}")
            
            # Initialize preprocessor
            try:
                from src.data_preprocessing import TextPreprocessor
                self.preprocessor = TextPreprocessor()
            except ImportError:
                try:
                    from data_preprocessing import TextPreprocessor
                    self.preprocessor = TextPreprocessor()
                except ImportError:
                    logger.warning("Could not import TextPreprocessor. Will initialize on first use.")
                    self.preprocessor = None
            
        except Exception as e:
            logger.error(f"Error loading model components: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess input text.
        
        Args:
            text: Input text string
            
        Returns:
            Preprocessed text
        """
        if self.preprocessor is None:
            try:
                from src.data_preprocessing import TextPreprocessor
                self.preprocessor = TextPreprocessor()
            except ImportError:
                try:
                    from data_preprocessing import TextPreprocessor
                    self.preprocessor = TextPreprocessor()
                except ImportError:
                    # Last resort: import from parent
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent))
                    from data_preprocessing import TextPreprocessor
                    self.preprocessor = TextPreprocessor()
        
        return self.preprocessor.preprocess_text(text)
    
    def predict_single(self, review_text: str) -> Dict[str, Union[str, float]]:
        """
        Make prediction for a single review.
        
        Args:
            review_text: Review text to classify
            
        Returns:
            Dictionary with prediction and confidence
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(review_text)
        
        # Vectorize text
        if self.vectorizer is not None:
            features = self.vectorizer.transform([processed_text]).toarray()
        else:
            raise ValueError("Vectorizer not loaded. Cannot transform text.")
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        
        # Get probability if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0
        
        # Decode label if encoder is available
        if self.label_encoder is not None:
            prediction_label = self.label_encoder.inverse_transform([prediction])[0]
        else:
            prediction_label = str(prediction)
        
        result = {
            'original_text': review_text,
            'processed_text': processed_text,
            'prediction': prediction_label,
            'prediction_numeric': int(prediction),
            'confidence': confidence
        }
        
        # Add probabilities if available
        if hasattr(self.model, 'predict_proba'):
            if self.label_encoder is not None:
                class_names = self.label_encoder.classes_
                result['probabilities'] = {
                    str(class_names[i]): float(prob) 
                    for i, prob in enumerate(probabilities)
                }
            else:
                result['probabilities'] = {
                    f'Class_{i}': float(prob) 
                    for i, prob in enumerate(probabilities)
                }
        
        return result
    
    def predict_batch(self, review_texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        """
        Make predictions for multiple reviews.
        
        Args:
            review_texts: List of review texts
            
        Returns:
            List of prediction dictionaries
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        logger.info(f"Making predictions for {len(review_texts)} reviews...")
        
        results = []
        
        for text in review_texts:
            try:
                result = self.predict_single(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error predicting review: {str(e)}")
                results.append({
                    'original_text': text,
                    'error': str(e)
                })
        
        logger.info(f"Batch prediction completed for {len(results)} reviews")
        
        return results
    
    def predict_from_dataframe(self, df: pd.DataFrame, 
                              text_column: str = 'review_text') -> pd.DataFrame:
        """
        Make predictions for reviews in a DataFrame.
        
        Args:
            df: Input DataFrame
            text_column: Name of the column containing review text
            
        Returns:
            DataFrame with predictions added
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        # Make predictions
        predictions = self.predict_batch(df[text_column].tolist())
        
        # Create results DataFrame
        results_df = df.copy()
        results_df['predicted_label'] = [p.get('prediction', None) for p in predictions]
        results_df['prediction_confidence'] = [p.get('confidence', None) for p in predictions]
        
        # Add probabilities if available
        if predictions and 'probabilities' in predictions[0]:
            for class_name in predictions[0]['probabilities'].keys():
                results_df[f'prob_{class_name}'] = [
                    p.get('probabilities', {}).get(class_name, None) 
                    for p in predictions
                ]
        
        return results_df
    
    def predict_from_csv(self, input_path: str, output_path: str = None,
                        text_column: str = 'review_text') -> pd.DataFrame:
        """
        Make predictions for reviews in a CSV file.
        
        Args:
            input_path: Path to input CSV file
            output_path: Path to save output CSV (optional)
            text_column: Name of the column containing review text
            
        Returns:
            DataFrame with predictions
        """
        logger.info(f"Loading data from {input_path}...")
        
        # Load data
        df = pd.read_csv(input_path)
        
        # Make predictions
        results_df = self.predict_from_dataframe(df, text_column)
        
        # Save results if output path provided
        if output_path:
            results_df.to_csv(output_path, index=False)
            logger.info(f"Predictions saved to {output_path}")
        
        return results_df
    
    def get_prediction_summary(self, predictions: List[Dict]) -> Dict:
        """
        Get summary statistics for batch predictions.
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        total = len(predictions)
        
        # Count predictions by class
        prediction_counts = {}
        confidences = []
        
        for pred in predictions:
            if 'prediction' in pred:
                label = pred['prediction']
                prediction_counts[label] = prediction_counts.get(label, 0) + 1
                
                if 'confidence' in pred:
                    confidences.append(pred['confidence'])
        
        summary = {
            'total_predictions': total,
            'prediction_distribution': prediction_counts,
            'average_confidence': np.mean(confidences) if confidences else None,
            'min_confidence': np.min(confidences) if confidences else None,
            'max_confidence': np.max(confidences) if confidences else None
        }
        
        return summary


def quick_predict(review_text: str, 
                 model_path: str,
                 vectorizer_path: str = None,
                 label_encoder_path: str = None) -> Dict:
    """
    Quick prediction function for single review.
    
    Args:
        review_text: Review text to classify
        model_path: Path to trained model
        vectorizer_path: Path to vectorizer
        label_encoder_path: Path to label encoder
        
    Returns:
        Prediction dictionary
    """
    predictor = ReviewPredictor()
    predictor.load_model(model_path, vectorizer_path, label_encoder_path)
    return predictor.predict_single(review_text)


def batch_predict_from_file(input_file: str,
                           output_file: str,
                           model_path: str,
                           vectorizer_path: str = None,
                           label_encoder_path: str = None,
                           text_column: str = 'review_text') -> pd.DataFrame:
    """
    Batch prediction from CSV file.
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path
        model_path: Path to trained model
        vectorizer_path: Path to vectorizer
        label_encoder_path: Path to label encoder
        text_column: Name of text column
        
    Returns:
        DataFrame with predictions
    """
    predictor = ReviewPredictor()
    predictor.load_model(model_path, vectorizer_path, label_encoder_path)
    return predictor.predict_from_csv(input_file, output_file, text_column)


if __name__ == "__main__":
    # Example usage
    print("Prediction module loaded successfully")
    print("\nUsage examples:")
    print("1. Single prediction:")
    print("   predictor = ReviewPredictor()")
    print("   predictor.load_model('models/best_model.pkl', 'models/vectorizer.pkl')")
    print("   result = predictor.predict_single('This product is amazing!')")
    print("\n2. Batch prediction:")
    print("   results = predictor.predict_batch(['Review 1', 'Review 2'])")
    print("\n3. CSV prediction:")
    print("   df = predictor.predict_from_csv('input.csv', 'output.csv')")
