"""
Streamlit Web Application
Interactive UI for fake review detection.
"""

import sys
import os
from pathlib import Path

# Add project root and src directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Download NLTK data if not present
try:
    import nltk
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('omw-1.4', quiet=True)
except Exception as e:
    pass  # Continue even if NLTK download fails

import streamlit as st
import pandas as pd
import numpy as np

# Handle optional dependencies gracefully
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from datetime import datetime

# Import project modules with error handling
try:
    from src import config
    from src.prediction import ReviewPredictor
    from src.utils import ensure_dir
except ImportError:
    # Try alternative import method
    try:
        import config
        from prediction import ReviewPredictor
        from utils import ensure_dir
    except ImportError as e:
        st.error(f"⚠️ Error importing modules: {str(e)}")
        st.info("Please ensure all files are in the correct directory structure.")

# Page configuration
st.set_page_config(
    page_title="Fake Review Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .fake-review {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .genuine-review {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_predictor():
    """Load the trained model and predictor."""
    try:
        predictor = ReviewPredictor()
        
        # Check if models exist
        if not config.BEST_MODEL_PATH.exists():
            st.error("⚠️ No trained model found. Please run main.py first to train the model.")
            return None
        
        predictor.load_model(
            str(config.BEST_MODEL_PATH),
            str(config.VECTORIZER_PATH),
            str(config.LABEL_ENCODER_PATH)
        )
        
        return predictor
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None


def display_prediction_result(result):
    """Display prediction result in a formatted box."""
    
    prediction = result['prediction']
    confidence = result['confidence']
    
    # Determine if fake or genuine
    is_fake = prediction == config.FAKE_LABEL
    
    # Choose styling
    box_class = "fake-review" if is_fake else "genuine-review"
    emoji = "⚠️ FAKE" if is_fake else "✅ GENUINE"
    color = "#f44336" if is_fake else "#4caf50"
    
    # Display result
    st.markdown(f"""
        <div class="result-box {box_class}">
            <h2 style="color: {color}; margin: 0;">{emoji} REVIEW</h2>
            <h3 style="margin-top: 0.5rem;">Confidence: {confidence:.1%}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Display probabilities if available
    if 'probabilities' in result:
        st.subheader("Prediction Probabilities")
        
        probs = result['probabilities']
        
        # Create gauge chart if plotly available
        if PLOTLY_AVAILABLE:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probs.get(config.FAKE_LABEL, 0) * 100,
                title={'text': "Fake Probability (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 50], 'color': "#e8f5e9"},
                        {'range': [50, 75], 'color': "#fff9c4"},
                        {'range': [75, 100], 'color': "#ffebee"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback visualization
            st.metric("Fake Probability", f"{probs.get(config.FAKE_LABEL, 0):.1%}")
        
        # Show probability table
        prob_df = pd.DataFrame({
            'Class': list(probs.keys()),
            'Probability': [f"{v:.2%}" for v in probs.values()]
        })
        st.table(prob_df)


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Fake Review Detector</h1>', unsafe_allow_html=True)
    st.markdown("""
        <p style="text-align: center; font-size: 1.2rem; color: #666;">
        Detect fake product reviews using machine learning
        </p>
    """, unsafe_allow_html=True)
    
    # Load predictor
    predictor = load_predictor()
    
    if predictor is None:
        st.stop()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Home", "🔮 Single Prediction", "📈 Model Info"]
    )
    
    # Home Page
    if page == "🏠 Home":
        st.markdown('<h2 class="sub-header">Welcome!</h2>', unsafe_allow_html=True)
        
        st.write("""
        This application uses machine learning to detect fake product reviews.
        
        ### Features:
        - **Single Prediction**: Analyze one review at a time
        - **Model Info**: View model performance metrics
        
        ### How it works:
        1. The system analyzes the text of a product review
        2. Extracts linguistic features and patterns
        3. Uses trained ML models to classify the review as fake or genuine
        4. Provides confidence scores for the prediction
        
        ### Get Started:
        Use the navigation menu on the left to start detecting fake reviews!
        """)
        
        # Display some statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <h3>6</h3>
                    <p>ML Models</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3>Real-time</h3>
                    <p>Prediction</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <h3>High</h3>
                    <p>Accuracy</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Single Prediction Page
    elif page == "🔮 Single Prediction":
        st.markdown('<h2 class="sub-header">Single Review Analysis</h2>', unsafe_allow_html=True)
        
        st.write("Enter a product review below to check if it's fake or genuine.")
        
        # Sample reviews for quick testing
        sample_reviews = {
            "Select a sample...": "",
            "Suspicious Review": "This product is absolutely amazing! Best purchase ever! Highly recommend! Five stars! Perfect! Excellent quality!",
            "Genuine Review": "The product is okay, does what it says. Shipping took a bit longer than expected but overall satisfied with the purchase."
        }
        
        sample_choice = st.selectbox("Try a sample review:", list(sample_reviews.keys()))
        
        # Text input
        review_text = st.text_area(
            "Review Text:",
            value=sample_reviews[sample_choice],
            height=150,
            placeholder="Type or paste a product review here..."
        )
        
        # Predict button
        if st.button("🔍 Analyze Review", type="primary"):
            if review_text.strip():
                with st.spinner("Analyzing review..."):
                    try:
                        result = predictor.predict_single(review_text)
                        
                        # Display result
                        st.success("Analysis complete!")
                        display_prediction_result(result)
                        
                        # Show processed text in expander
                        with st.expander("View Processed Text"):
                            st.write("**Original:**")
                            st.text(result['original_text'])
                            st.write("**Processed:**")
                            st.text(result['processed_text'])
                    
                    except Exception as e:
                        st.error(f"Error during prediction: {str(e)}")
            else:
                st.warning("Please enter a review text.")
    
    # Model Info Page
    elif page == "📈 Model Info":
        st.markdown('<h2 class="sub-header">Model Information</h2>', unsafe_allow_html=True)
        
        st.write("Information about the trained models and their performance.")
        
        # Load training results if available
        results_path = config.MODELS_DIR / 'training_results.json'
        comparison_path = config.MODELS_DIR / 'model_comparison.csv'
        
        if results_path.exists():
            import json
            
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            # Display best model info
            st.subheader("🏆 Best Model")
            
            best_model = results['best_model']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Model Name", best_model['name'])
                st.metric("Accuracy", f"{best_model['test_metrics']['accuracy']:.2%}")
            
            with col2:
                st.metric("CV Score", f"{best_model['cv_score']:.2%}")
                st.metric("F1-Score", f"{best_model['test_metrics']['f1_score']:.2%}")
            
            # Model comparison
            if comparison_path.exists():
                st.subheader("📊 Model Comparison")
                
                comparison_df = pd.read_csv(comparison_path)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Bar chart
                if PLOTLY_AVAILABLE:
                    fig = px.bar(
                        comparison_df,
                        x='Model',
                        y=['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                        title='Model Performance Comparison',
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to dataframe display
                    st.bar_chart(comparison_df.set_index('Model'))
            
            # Dataset info
            st.subheader("📁 Dataset Information")
            
            dataset = results['dataset']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Samples", dataset['total_samples'])
            
            with col2:
                st.metric("Training Samples", dataset['training_samples'])
            
            with col3:
                st.metric("Testing Samples", dataset['testing_samples'])
        
        else:
            st.warning("No training results found. Please run main.py to train the models first.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <p style="text-align: center; color: #666;">
        Made with ❤️ using Streamlit | Fake Review Detector v1.0
        </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
