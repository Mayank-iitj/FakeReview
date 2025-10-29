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
        ["🏠 Home", "🔮 Single Prediction", "� URL Analysis", "�📊 Batch Prediction", "📈 Model Info"]
    )
    
    # Home Page
    if page == "🏠 Home":
        st.markdown('<h2 class="sub-header">Welcome!</h2>', unsafe_allow_html=True)
        
        st.write("""
        This application uses machine learning to detect fake product reviews.
        
        ### Features:
        - **Single Prediction**: Analyze one review at a time
        - **URL Analysis**: Scrape and analyze reviews from product URLs
        - **Batch Prediction**: Upload a CSV file to analyze multiple reviews
        - **Model Info**: View model performance metrics
        
        ### How it works:
        1. The system analyzes the text of a product review
        2. Extracts linguistic features and patterns
        3. Uses trained ML models to classify the review as fake or genuine
        4. Provides confidence scores for the prediction
        
        ### Supported Platforms for URL Analysis:
        - Amazon (amazon.com, amazon.in, amazon.co.uk, etc.)
        - Flipkart (flipkart.com)
        - eBay (ebay.com, ebay.in, etc.)
        
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
    
    # URL Analysis Page
    elif page == "🔗 URL Analysis":
        st.markdown('<h2 class="sub-header">Product URL Analysis</h2>', unsafe_allow_html=True)
        
        st.write("Enter a product URL from supported e-commerce platforms to analyze all reviews.")
        
        # Import web scraper
        try:
            from src.web_scraper import ReviewScraper
        except ImportError:
            try:
                from web_scraper import ReviewScraper
            except ImportError:
                st.error("Web scraper module not found. Please ensure web_scraper.py is in the src directory.")
                st.stop()
        
        # Supported platforms info
        with st.expander("ℹ️ Supported Platforms"):
            st.markdown("""
            - **Amazon**: amazon.com, amazon.in, amazon.co.uk, amazon.de, amazon.fr
            - **Flipkart**: flipkart.com
            - **eBay**: ebay.com, ebay.in, ebay.co.uk
            
            **Note**: Web scraping is subject to the platform's terms of service and robots.txt.
            This feature is for educational/research purposes.
            """)
        
        # URL input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            product_url = st.text_input(
                "Product URL:",
                placeholder="https://www.amazon.com/product/...",
                help="Paste the full product URL from a supported platform"
            )
        
        with col2:
            max_reviews = st.number_input(
                "Max Reviews:",
                min_value=10,
                max_value=100,
                value=50,
                step=10,
                help="Maximum number of reviews to analyze"
            )
        
        # Sample URLs for testing
        st.markdown("**Quick Test URLs:**")
        st.caption("You can try these sample URLs for testing (subject to availability)")
        
        # Analyze button
        if st.button("🔍 Scrape & Analyze Reviews", type="primary"):
            if product_url.strip():
                # Initialize scraper
                scraper = ReviewScraper(max_reviews=max_reviews, delay=1.5)
                
                # Identify platform
                platform = scraper.identify_platform(product_url)
                
                if not platform:
                    st.error("❌ Unsupported platform. Please use a URL from Amazon, Flipkart, or eBay.")
                    st.stop()
                
                st.info(f"🔍 Detected platform: **{platform.title()}**")
                
                # Scrape reviews
                with st.spinner(f"Scraping reviews from {platform.title()}... This may take a minute."):
                    try:
                        reviews = scraper.scrape_reviews(product_url)
                        
                        if not reviews:
                            st.warning("⚠️ No reviews found. The page might have changed or there are no reviews available.")
                            st.info("**Troubleshooting tips:**")
                            st.markdown("""
                            - Verify the URL is correct and the product has reviews
                            - Some platforms may block automated requests
                            - Try a different product or platform
                            - For production use, consider using official APIs
                            """)
                            st.stop()
                        
                        st.success(f"✅ Successfully scraped {len(reviews)} reviews!")
                        
                        # Convert to DataFrame
                        reviews_df = scraper.reviews_to_dataframe(reviews)
                        
                        # Show preview
                        with st.expander("📋 View Scraped Reviews", expanded=False):
                            st.dataframe(reviews_df, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"❌ Error scraping reviews: {str(e)}")
                        st.info("This might be due to:")
                        st.markdown("""
                        - Network connectivity issues
                        - Website structure changes
                        - Anti-scraping measures by the platform
                        - Rate limiting
                        
                        **Recommendation**: Try again later or use the Batch Prediction feature with a CSV file.
                        """)
                        st.stop()
                
                # Analyze reviews
                with st.spinner(f"Analyzing {len(reviews)} reviews..."):
                    try:
                        # Predict on all reviews
                        results_df = predictor.predict_from_dataframe(reviews_df, 'text')
                        
                        st.success("✅ Analysis complete!")
                        
                        # Display summary
                        st.markdown("---")
                        st.markdown('<h3 class="sub-header">📊 Analysis Results</h3>', unsafe_allow_html=True)
                        
                        # Key metrics
                        total = len(results_df)
                        fake_count = (results_df['predicted_label'] == config.FAKE_LABEL).sum()
                        genuine_count = (results_df['predicted_label'] == config.GENUINE_LABEL).sum()
                        fake_percentage = (fake_count / total * 100) if total > 0 else 0
                        
                        # Display metrics in columns
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Reviews", total)
                        
                        with col2:
                            st.metric("🚫 Fake Reviews", fake_count, f"{fake_percentage:.1f}%")
                        
                        with col3:
                            st.metric("✅ Genuine Reviews", genuine_count, f"{100-fake_percentage:.1f}%")
                        
                        with col4:
                            avg_confidence = results_df['confidence'].mean()
                            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
                        
                        # Alert if high fake percentage
                        if fake_percentage > 30:
                            st.error(f"⚠️ **High Alert**: {fake_percentage:.1f}% of reviews appear to be fake! This product may have suspicious review activity.")
                        elif fake_percentage > 15:
                            st.warning(f"⚠️ **Caution**: {fake_percentage:.1f}% of reviews appear to be fake. Review this product carefully.")
                        else:
                            st.success(f"✅ **Good**: Only {fake_percentage:.1f}% of reviews appear to be fake. This product seems trustworthy.")
                        
                        # Visualization
                        st.markdown("### 📈 Visual Analysis")
                        
                        if PLOTLY_AVAILABLE:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Pie chart
                                fig_pie = px.pie(
                                    values=[fake_count, genuine_count],
                                    names=['Fake', 'Genuine'],
                                    title='Review Distribution',
                                    color_discrete_sequence=['#f44336', '#4caf50'],
                                    hole=0.4
                                )
                                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            with col2:
                                # Confidence distribution
                                fig_hist = px.histogram(
                                    results_df,
                                    x='confidence',
                                    color='predicted_label',
                                    title='Confidence Distribution',
                                    labels={'confidence': 'Confidence Score', 'count': 'Number of Reviews'},
                                    color_discrete_map={config.FAKE_LABEL: '#f44336', config.GENUINE_LABEL: '#4caf50'},
                                    nbins=20
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                        
                        # Detailed results table
                        st.markdown("### 📋 Detailed Results")
                        
                        # Add filter
                        filter_option = st.selectbox(
                            "Filter reviews:",
                            ["All Reviews", "Fake Reviews Only", "Genuine Reviews Only"]
                        )
                        
                        if filter_option == "Fake Reviews Only":
                            display_df = results_df[results_df['predicted_label'] == config.FAKE_LABEL]
                        elif filter_option == "Genuine Reviews Only":
                            display_df = results_df[results_df['predicted_label'] == config.GENUINE_LABEL]
                        else:
                            display_df = results_df
                        
                        # Display with formatting
                        st.dataframe(
                            display_df.style.applymap(
                                lambda x: 'background-color: #ffebee' if x == config.FAKE_LABEL else 'background-color: #e8f5e9',
                                subset=['predicted_label']
                            ),
                            use_container_width=True
                        )
                        
                        # Download button
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Full Analysis",
                            data=csv,
                            file_name=f"review_analysis_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Top suspicious reviews
                        if fake_count > 0:
                            st.markdown("### 🚨 Most Suspicious Reviews")
                            st.caption("Reviews with highest confidence of being fake")
                            
                            fake_reviews = results_df[results_df['predicted_label'] == config.FAKE_LABEL]
                            top_suspicious = fake_reviews.nlargest(5, 'confidence')
                            
                            for idx, row in top_suspicious.iterrows():
                                with st.expander(f"Review #{idx+1} - Confidence: {row['confidence']:.1%}"):
                                    st.write("**Review Text:**")
                                    st.write(row['text'])
                                    if 'rating' in row:
                                        st.write(f"**Rating:** {row['rating']}")
                                    if 'date' in row:
                                        st.write(f"**Date:** {row['date']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error analyzing reviews: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            else:
                st.warning("⚠️ Please enter a product URL.")
    
    # Batch Prediction Page
    elif page == "📊 Batch Prediction":
        st.markdown('<h2 class="sub-header">Batch Review Analysis</h2>', unsafe_allow_html=True)
        
        st.write("Upload a CSV file containing multiple reviews for batch analysis.")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="CSV file should have a column named 'review_text'"
        )
        
        if uploaded_file is not None:
            try:
                # Load data
                df = pd.read_csv(uploaded_file)
                
                st.success(f"File uploaded successfully! Found {len(df)} reviews.")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Select text column
                text_column = st.selectbox(
                    "Select the column containing review text:",
                    df.columns.tolist()
                )
                
                # Analyze button
                if st.button("📊 Analyze All Reviews", type="primary"):
                    with st.spinner(f"Analyzing {len(df)} reviews..."):
                        try:
                            # Make predictions
                            results_df = predictor.predict_from_dataframe(df, text_column)
                            
                            # Display summary
                            st.success("Batch analysis complete!")
                            
                            st.subheader("Results Summary")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                total = len(results_df)
                                st.metric("Total Reviews", total)
                            
                            with col2:
                                fake_count = (results_df['predicted_label'] == config.FAKE_LABEL).sum()
                                st.metric("Fake Reviews", fake_count)
                            
                            with col3:
                                genuine_count = (results_df['predicted_label'] == config.GENUINE_LABEL).sum()
                                st.metric("Genuine Reviews", genuine_count)
                            
                            # Pie chart
                            if PLOTLY_AVAILABLE:
                                fig = px.pie(
                                    values=[fake_count, genuine_count],
                                    names=['Fake', 'Genuine'],
                                    title='Review Distribution',
                                    color_discrete_sequence=['#f44336', '#4caf50']
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                # Fallback to simple display
                                st.write(f"**Fake Reviews:** {fake_count}")
                                st.write(f"**Genuine Reviews:** {genuine_count}")
                                st.progress(fake_count / total if total > 0 else 0)
                            
                            # Show results table
                            st.subheader("Detailed Results")
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Download button
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name=f"fake_review_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        except Exception as e:
                            st.error(f"Error during batch prediction: {str(e)}")
            
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
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
