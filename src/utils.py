"""
Utility Functions Module
Contains helper functions for the fake review detector project.
"""

import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_logging(log_file: str = None, level: str = 'INFO'):
    """
    Setup logging configuration.
    
    Args:
        log_file: Path to log file (optional)
        level: Logging level
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=getattr(logging, level),
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=getattr(logging, level),
            format=log_format
        )


def create_timestamp() -> str:
    """
    Create a timestamp string for file naming.
    
    Returns:
        Timestamp string
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def ensure_dir(directory: str):
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def save_results(results: dict, output_path: str):
    """
    Save results dictionary to JSON file.
    
    Args:
        results: Results dictionary
        output_path: Path to save results
    """
    ensure_dir(os.path.dirname(output_path))
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4, default=str)
    
    logger.info(f"Results saved to {output_path}")


def load_results(input_path: str) -> dict:
    """
    Load results from JSON file.
    
    Args:
        input_path: Path to results file
        
    Returns:
        Results dictionary
    """
    with open(input_path, 'r') as f:
        results = json.load(f)
    
    logger.info(f"Results loaded from {input_path}")
    return results


def print_section_header(title: str, width: int = 80):
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        width: Width of the header
    """
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")


def format_time(seconds: float) -> str:
    """
    Format time in seconds to readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def display_dataframe_info(df: pd.DataFrame, name: str = "DataFrame"):
    """
    Display comprehensive information about a DataFrame.
    
    Args:
        df: Input DataFrame
        name: Name for the DataFrame
    """
    print_section_header(f"{name} Information")
    
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nColumn Types:")
    print(df.dtypes)
    
    print(f"\nMissing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values")
    
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    
    print(f"\nStatistical Summary:")
    print(df.describe())


def calculate_class_balance(y: np.ndarray) -> dict:
    """
    Calculate class balance metrics.
    
    Args:
        y: Array of labels
        
    Returns:
        Dictionary with class balance information
    """
    unique, counts = np.unique(y, return_counts=True)
    total = len(y)
    
    balance_info = {
        'total_samples': total,
        'classes': {}
    }
    
    for label, count in zip(unique, counts):
        balance_info['classes'][str(label)] = {
            'count': int(count),
            'percentage': float(count / total * 100)
        }
    
    # Calculate imbalance ratio
    if len(counts) == 2:
        balance_info['imbalance_ratio'] = float(max(counts) / min(counts))
    
    return balance_info


def create_sample_dataset(output_path: str, n_samples: int = 100):
    """
    Create a sample dataset for testing.
    
    Args:
        output_path: Path to save the sample dataset
        n_samples: Number of samples to generate
    """
    # Sample fake reviews (computer-generated patterns)
    fake_reviews = [
        "This product is absolutely amazing! Best purchase ever! Highly recommend! Five stars!",
        "Excellent quality and fast shipping. Very satisfied with this purchase. Great value!",
        "Perfect product! Exceeded all my expectations. Will definitely buy again. Thank you!",
        "Outstanding item! Superior quality and performance. Highly recommended. A must buy!",
        "Fantastic product with great features. Shipping was quick. Very happy customer!",
    ]
    
    # Sample genuine reviews (more natural, varied)
    genuine_reviews = [
        "It's okay, does what it says but nothing special. Arrived a bit late though.",
        "Pretty good overall. Had some minor issues with the setup but works fine now.",
        "Not bad for the price. Quality could be better but it serves its purpose.",
        "Works as expected. Not the best I've seen but decent enough for everyday use.",
        "It's alright. Took some time to figure out how to use it properly.",
    ]
    
    # Generate dataset
    data = []
    
    for i in range(n_samples // 2):
        # Add fake review
        data.append({
            'review_text': np.random.choice(fake_reviews) + f" Review {i}.",
            'rating': np.random.choice([5, 5, 4, 5]),  # Biased towards 5
            'label': 'CG'
        })
        
        # Add genuine review
        data.append({
            'review_text': np.random.choice(genuine_reviews) + f" Comment {i}.",
            'rating': np.random.choice([3, 4, 5, 2, 3]),  # More varied
            'label': 'OR'
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save
    ensure_dir(os.path.dirname(output_path))
    df.to_csv(output_path, index=False)
    
    logger.info(f"Sample dataset with {len(df)} reviews created at {output_path}")
    
    return df


def validate_dataset(df: pd.DataFrame, 
                     text_column: str = 'review_text',
                     label_column: str = 'label') -> bool:
    """
    Validate dataset has required columns and proper format.
    
    Args:
        df: Input DataFrame
        text_column: Name of text column
        label_column: Name of label column
        
    Returns:
        True if valid, raises ValueError if not
    """
    # Check required columns exist
    required_columns = [text_column, label_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for empty dataset
    if len(df) == 0:
        raise ValueError("Dataset is empty")
    
    # Check for missing values in critical columns
    if df[text_column].isnull().any():
        logger.warning(f"Found missing values in {text_column}")
    
    if df[label_column].isnull().any():
        raise ValueError(f"Found missing values in {label_column}")
    
    # Check label values
    unique_labels = df[label_column].unique()
    logger.info(f"Found {len(unique_labels)} unique labels: {unique_labels}")
    
    if len(unique_labels) < 2:
        raise ValueError("Need at least 2 classes for classification")
    
    logger.info("Dataset validation passed")
    return True


def print_model_summary(model_name: str, metrics: dict, training_info: dict = None):
    """
    Print a formatted summary of model performance.
    
    Args:
        model_name: Name of the model
        metrics: Dictionary of metrics
        training_info: Dictionary of training information
    """
    print_section_header(f"{model_name} Summary")
    
    print("Performance Metrics:")
    print(f"  Accuracy:  {metrics.get('accuracy', 0):.4f}")
    print(f"  Precision: {metrics.get('precision', 0):.4f}")
    print(f"  Recall:    {metrics.get('recall', 0):.4f}")
    print(f"  F1-Score:  {metrics.get('f1_score', 0):.4f}")
    
    if 'roc_auc' in metrics:
        print(f"  ROC AUC:   {metrics['roc_auc']:.4f}")
    
    if training_info:
        print(f"\nTraining Information:")
        if 'training_time' in training_info:
            print(f"  Training Time: {format_time(training_info['training_time'])}")
        if 'cv_score' in training_info:
            print(f"  CV Score: {training_info['cv_score']:.4f}")
        if 'best_params' in training_info and training_info['best_params']:
            print(f"  Best Parameters: {training_info['best_params']}")


if __name__ == "__main__":
    # Example usage
    print("Utility functions loaded successfully")
    
    # Create sample dataset
    sample_path = "data/sample_reviews.csv"
    df = create_sample_dataset(sample_path, n_samples=20)
    
    print("\nSample dataset created:")
    print(df.head())
