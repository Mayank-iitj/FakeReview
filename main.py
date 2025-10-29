"""
Main Training Pipeline
Orchestrates the entire fake review detection workflow.
"""

import sys
import os
from pathlib import Path

# Add project root and src directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime

# Import project modules with error handling
try:
    from src import config
    from src.data_preprocessing import load_and_preprocess_data
    from src.feature_extraction import extract_features
    from src.model_training import ModelTrainer, split_data
    from src.evaluation import (
        ModelEvaluator, plot_data_distribution, 
        plot_text_length_distribution
    )
    from src.utils import (
        print_section_header, ensure_dir, save_results,
        validate_dataset, print_model_summary, format_time,
        create_sample_dataset
    )
except ImportError:
    # Try alternative import method
    import config
    from data_preprocessing import load_and_preprocess_data
    from feature_extraction import extract_features
    from model_training import ModelTrainer, split_data
    from evaluation import (
        ModelEvaluator, plot_data_distribution, 
        plot_text_length_distribution
    )
    from utils import (
        print_section_header, ensure_dir, save_results,
        validate_dataset, print_model_summary, format_time,
        create_sample_dataset
    )

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline."""
    
    print_section_header("FAKE REVIEW DETECTOR - Training Pipeline")
    start_time = time.time()
    
    # ========== Step 1: Check and Load Data ==========
    print_section_header("Step 1: Loading Data")
    
    # Check if data file exists, create sample if not
    if not config.RAW_DATA_PATH.exists():
        logger.warning(f"Data file not found at {config.RAW_DATA_PATH}")
        logger.info("Creating sample dataset for demonstration...")
        create_sample_dataset(str(config.RAW_DATA_PATH), n_samples=1000)
    
    # Load and validate data
    logger.info(f"Loading data from {config.RAW_DATA_PATH}...")
    df = pd.read_csv(config.RAW_DATA_PATH)
    logger.info(f"Loaded {len(df)} reviews")
    
    # Validate dataset
    validate_dataset(df, config.TEXT_COLUMN, config.LABEL_COLUMN)
    
    # Display data info
    print("\nDataset Overview:")
    print(f"Total reviews: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nClass distribution:")
    print(df[config.LABEL_COLUMN].value_counts())
    
    # ========== Step 2: Visualize Data ==========
    print_section_header("Step 2: Data Visualization")
    
    # Plot class distribution
    plot_data_distribution(
        df, 
        config.LABEL_COLUMN,
        save_path=str(config.VISUALIZATION_DIR / 'class_distribution.png')
    )
    
    # Plot text length distribution
    plot_text_length_distribution(
        df,
        config.TEXT_COLUMN,
        config.LABEL_COLUMN,
        save_path=str(config.VISUALIZATION_DIR / 'text_length_distribution.png')
    )
    
    logger.info("Data visualizations saved")
    
    # ========== Step 3: Preprocess Data ==========
    print_section_header("Step 3: Data Preprocessing")
    
    df_processed = load_and_preprocess_data(
        file_path=str(config.RAW_DATA_PATH),
        text_column=config.TEXT_COLUMN,
        label_column=config.LABEL_COLUMN,
        remove_stopwords=config.REMOVE_STOPWORDS,
        apply_stemming=config.APPLY_STEMMING,
        apply_lemmatization=config.APPLY_LEMMATIZATION
    )
    
    logger.info(f"Preprocessing completed. {len(df_processed)} reviews ready for training")
    
    # Save processed data
    df_processed.to_csv(config.PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed data saved to {config.PROCESSED_DATA_PATH}")
    
    # ========== Step 4: Feature Extraction ==========
    print_section_header("Step 4: Feature Extraction")
    
    features, feature_extractor = extract_features(
        df_processed,
        text_column='processed_text',
        method=config.FEATURE_EXTRACTION_METHOD,
        max_features=config.MAX_FEATURES,
        ngram_range=config.NGRAM_RANGE,
        min_df=config.MIN_DF,
        max_df=config.MAX_DF,
        include_additional_features=True
    )
    
    logger.info(f"Feature extraction completed. Feature shape: {features.shape}")
    
    # Save vectorizer
    feature_extractor.save_vectorizer(str(config.VECTORIZER_PATH))
    
    # ========== Step 5: Prepare Train/Test Split ==========
    print_section_header("Step 5: Train/Test Split")
    
    # Initialize trainer for label encoding
    trainer = ModelTrainer(random_state=config.RANDOM_STATE)
    
    # Encode labels
    y = trainer.encode_labels(df_processed[config.LABEL_COLUMN])
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(
        features, y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE
    )
    
    logger.info(f"Training set: {X_train.shape[0]} samples")
    logger.info(f"Testing set: {X_test.shape[0]} samples")
    
    # Save label encoder
    trainer.save_label_encoder(str(config.LABEL_ENCODER_PATH))
    
    # ========== Step 6: Train Models ==========
    print_section_header("Step 6: Training Models")
    
    training_results = trainer.train_all_models(
        X_train, y_train,
        models_to_train=config.MODELS_TO_TRAIN,
        hyperparameter_tuning=True,
        cv_folds=config.CROSS_VALIDATION_FOLDS
    )
    
    logger.info("All models trained successfully")
    
    # ========== Step 7: Evaluate Models ==========
    print_section_header("Step 7: Model Evaluation")
    
    # Initialize evaluator
    evaluator = ModelEvaluator(class_names=[config.GENUINE_LABEL, config.FAKE_LABEL])
    
    # Evaluate each model
    evaluation_results = {}
    
    for model_name in trainer.trained_models.keys():
        logger.info(f"\nEvaluating {model_name}...")
        
        # Get predictions
        y_pred = trainer.predict(model_name, X_test)
        
        # Get probabilities if available
        try:
            y_pred_proba = trainer.predict_proba(model_name, X_test)
        except:
            y_pred_proba = None
        
        # Evaluate
        result = evaluator.evaluate_model(
            y_test, y_pred, y_pred_proba,
            model_name=model_name,
            save_dir=str(config.VISUALIZATION_DIR)
        )
        
        evaluation_results[model_name] = result
        
        # Print summary
        print_model_summary(
            model_name,
            result['metrics'],
            training_results.get(model_name, {})
        )
    
    # ========== Step 8: Compare Models ==========
    print_section_header("Step 8: Model Comparison")
    
    comparison_df = evaluator.compare_models(
        evaluation_results,
        save_path=str(config.VISUALIZATION_DIR / 'model_comparison.png')
    )
    
    # ========== Step 9: Save Best Model ==========
    print_section_header("Step 9: Saving Best Model")
    
    logger.info(f"Best model: {trainer.best_model_name}")
    logger.info(f"Best CV score: {trainer.best_score:.4f}")
    
    # Save best model
    trainer.save_best_model(str(config.BEST_MODEL_PATH))
    
    # Save all models
    for model_name in trainer.trained_models.keys():
        model_path = config.MODELS_DIR / f'{model_name}_model.pkl'
        trainer.save_model(model_name, str(model_path))
    
    logger.info("All models saved successfully")
    
    # ========== Step 10: Save Results Summary ==========
    print_section_header("Step 10: Saving Results")
    
    # Compile results
    results_summary = {
        'timestamp': datetime.now().isoformat(),
        'dataset': {
            'total_samples': len(df),
            'training_samples': len(X_train),
            'testing_samples': len(X_test),
            'num_features': features.shape[1]
        },
        'best_model': {
            'name': trainer.best_model_name,
            'cv_score': float(trainer.best_score),
            'test_metrics': {
                k: float(v) if isinstance(v, (int, float, np.number)) else v
                for k, v in evaluation_results[trainer.best_model_name]['metrics'].items()
            }
        },
        'all_models': {}
    }
    
    # Add all model results
    for model_name, result in evaluation_results.items():
        results_summary['all_models'][model_name] = {
            'metrics': {
                k: float(v) if isinstance(v, (int, float, np.number)) else v
                for k, v in result['metrics'].items()
            },
            'training_info': training_results.get(model_name, {})
        }
    
    # Save results
    results_path = config.MODELS_DIR / 'training_results.json'
    save_results(results_summary, str(results_path))
    
    # Save comparison DataFrame
    comparison_path = config.MODELS_DIR / 'model_comparison.csv'
    comparison_df.to_csv(comparison_path, index=False)
    
    # ========== Final Summary ==========
    total_time = time.time() - start_time
    
    print_section_header("Training Pipeline Completed!")
    
    print(f"Total execution time: {format_time(total_time)}")
    print(f"\nBest Model: {trainer.best_model_name}")
    print(f"Test Accuracy: {evaluation_results[trainer.best_model_name]['metrics']['accuracy']:.4f}")
    print(f"\nAll results saved to: {config.MODELS_DIR}")
    print(f"Visualizations saved to: {config.VISUALIZATION_DIR}")
    
    print("\n" + "="*80)
    print("Next Steps:")
    print("  1. Review visualizations in the 'visualizations' folder")
    print("  2. Check model comparison results")
    print("  3. Run the Streamlit app: streamlit run app.py")
    print("  4. Use the best model for predictions")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}", exc_info=True)
        sys.exit(1)
