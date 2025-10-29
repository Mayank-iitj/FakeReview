"""
Evaluation Module
Implements comprehensive model evaluation with metrics and visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc,
    roc_auc_score
)
from typing import Dict, List, Tuple, Any
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100


class ModelEvaluator:
    """
    A class for evaluating machine learning models with comprehensive metrics and visualizations.
    """
    
    def __init__(self, class_names: List[str] = None):
        """
        Initialize the ModelEvaluator.
        
        Args:
            class_names: List of class names for visualization
        """
        self.class_names = class_names if class_names else ['Class 0', 'Class 1']
        self.evaluation_results = {}
        
        logger.info("ModelEvaluator initialized successfully")
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                         model_name: str = 'Model') -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0)
        }
        
        # Calculate per-class metrics
        precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
        
        for i, class_name in enumerate(self.class_names):
            if i < len(precision_per_class):
                metrics[f'precision_{class_name}'] = precision_per_class[i]
                metrics[f'recall_{class_name}'] = recall_per_class[i]
                metrics[f'f1_{class_name}'] = f1_per_class[i]
        
        logger.info(f"\n{model_name} Metrics:")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info(f"F1-Score: {metrics['f1_score']:.4f}")
        
        return metrics
    
    def generate_classification_report(self, y_true: np.ndarray, y_pred: np.ndarray) -> str:
        """
        Generate detailed classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Classification report as string
        """
        report = classification_report(
            y_true, y_pred,
            target_names=self.class_names,
            zero_division=0
        )
        
        return report
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray,
                             model_name: str = 'Model',
                             save_path: str = None,
                             normalize: bool = False):
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_name: Name of the model
            save_path: Path to save the plot
            normalize: Whether to normalize the confusion matrix
        """
        cm = confusion_matrix(y_true, y_pred)
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            fmt = '.2%'
            title = f'Normalized Confusion Matrix - {model_name}'
        else:
            fmt = 'd'
            title = f'Confusion Matrix - {model_name}'
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names,
                   cbar_kws={'label': 'Count' if not normalize else 'Proportion'})
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        
        plt.close()
    
    def plot_roc_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                      model_name: str = 'Model',
                      save_path: str = None):
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            model_name: Name of the model
            save_path: Path to save the plot
        """
        # For binary classification
        if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] == 2:
            y_pred_proba = y_pred_proba[:, 1]
        
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {model_name}', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"ROC curve saved to {save_path}")
        
        plt.close()
    
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray,
                      y_pred_proba: np.ndarray = None,
                      model_name: str = 'Model',
                      save_dir: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive model evaluation.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            model_name: Name of the model
            save_dir: Directory to save plots
            
        Returns:
            Dictionary of evaluation results
        """
        logger.info(f"\nEvaluating {model_name}...")
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, model_name)
        
        # Generate classification report
        report = self.generate_classification_report(y_true, y_pred)
        
        # Create save directory if specified
        if save_dir:
            Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        # Plot confusion matrix
        if save_dir:
            cm_path = Path(save_dir) / f'{model_name}_confusion_matrix.png'
            self.plot_confusion_matrix(y_true, y_pred, model_name, str(cm_path))
        else:
            self.plot_confusion_matrix(y_true, y_pred, model_name)
        
        # Plot ROC curve if probabilities are available
        if y_pred_proba is not None:
            try:
                roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1] if y_pred_proba.ndim == 2 else y_pred_proba)
                metrics['roc_auc'] = roc_auc
                
                if save_dir:
                    roc_path = Path(save_dir) / f'{model_name}_roc_curve.png'
                    self.plot_roc_curve(y_true, y_pred_proba, model_name, str(roc_path))
                else:
                    self.plot_roc_curve(y_true, y_pred_proba, model_name)
            except Exception as e:
                logger.warning(f"Could not plot ROC curve: {str(e)}")
        
        # Store results
        results = {
            'metrics': metrics,
            'classification_report': report
        }
        
        self.evaluation_results[model_name] = results
        
        # Print classification report
        logger.info(f"\n{model_name} Classification Report:")
        logger.info(f"\n{report}")
        
        return results
    
    def compare_models(self, results: Dict[str, Dict], save_path: str = None):
        """
        Compare multiple models and visualize their performance.
        
        Args:
            results: Dictionary of model results
            save_path: Path to save the comparison plot
        """
        # Prepare data for comparison
        model_names = []
        accuracies = []
        precisions = []
        recalls = []
        f1_scores = []
        
        for model_name, result in results.items():
            if 'metrics' in result:
                metrics = result['metrics']
                model_names.append(model_name)
                accuracies.append(metrics.get('accuracy', 0))
                precisions.append(metrics.get('precision', 0))
                recalls.append(metrics.get('recall', 0))
                f1_scores.append(metrics.get('f1_score', 0))
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame({
            'Model': model_names,
            'Accuracy': accuracies,
            'Precision': precisions,
            'Recall': recalls,
            'F1-Score': f1_scores
        })
        
        # Plot comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(model_names))
        width = 0.2
        
        ax.bar(x - 1.5*width, accuracies, width, label='Accuracy', color='skyblue')
        ax.bar(x - 0.5*width, precisions, width, label='Precision', color='lightgreen')
        ax.bar(x + 0.5*width, recalls, width, label='Recall', color='lightcoral')
        ax.bar(x + 1.5*width, f1_scores, width, label='F1-Score', color='plum')
        
        ax.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Model comparison plot saved to {save_path}")
        
        plt.close()
        
        # Print comparison table
        logger.info("\n" + "="*80)
        logger.info("MODEL PERFORMANCE COMPARISON")
        logger.info("="*80)
        logger.info(comparison_df.to_string(index=False))
        logger.info("="*80)
        
        return comparison_df


def plot_data_distribution(df: pd.DataFrame, label_column: str, save_path: str = None):
    """
    Plot the distribution of classes in the dataset.
    
    Args:
        df: Input DataFrame
        label_column: Name of the label column
        save_path: Path to save the plot
    """
    plt.figure(figsize=(8, 6))
    
    class_counts = df[label_column].value_counts()
    
    # Create bar plot
    ax = class_counts.plot(kind='bar', color=['skyblue', 'lightcoral'])
    plt.title('Class Distribution in Dataset', fontsize=14, fontweight='bold')
    plt.xlabel('Class', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=0)
    
    # Add value labels on bars
    for i, v in enumerate(class_counts):
        ax.text(i, v + 50, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Class distribution plot saved to {save_path}")
    
    plt.close()


def plot_text_length_distribution(df: pd.DataFrame, 
                                  text_column: str,
                                  label_column: str,
                                  save_path: str = None):
    """
    Plot the distribution of text lengths by class.
    
    Args:
        df: Input DataFrame
        text_column: Name of the text column
        label_column: Name of the label column
        save_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    
    # Calculate text lengths
    df['text_length'] = df[text_column].apply(lambda x: len(str(x)))
    
    # Plot distributions by class
    for label in df[label_column].unique():
        subset = df[df[label_column] == label]['text_length']
        plt.hist(subset, bins=50, alpha=0.6, label=f'{label}')
    
    plt.title('Text Length Distribution by Class', fontsize=14, fontweight='bold')
    plt.xlabel('Text Length (characters)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Text length distribution plot saved to {save_path}")
    
    plt.close()
    
    # Remove temporary column
    df.drop('text_length', axis=1, inplace=True)


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create dummy predictions
    y_pred = np.random.randint(0, 2, size=len(y_test))
    y_pred_proba = np.random.rand(len(y_test), 2)
    y_pred_proba = y_pred_proba / y_pred_proba.sum(axis=1, keepdims=True)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(class_names=['Fake', 'Genuine'])
    
    # Evaluate model
    results = evaluator.evaluate_model(y_test, y_pred, y_pred_proba, model_name='Example Model')
    
    print("\nEvaluation Results:")
    print(results)
