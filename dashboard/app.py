"""Streamlit admin dashboard."""
import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from loguru import logger

from app.api_client import APIClient, APIError, get_client, health_check_sync
from app.utils import (
    validate_csv_file,
    validate_review_input,
    map_api_error_to_user_message,
    check_response_structure,
    format_percentage,
    format_confidence,
    safe_get,
    parse_batch_results,
)
from dashboard.components import (
    render_review_card,
    render_error_banner,
    render_health_status,
    render_loading_spinner,
    render_success_message,
    render_info_message,
    render_warning_message,
    render_download_button,
)

# Page configuration
st.set_page_config(
    page_title="Fake Review Detection Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .fake-review {
            background-color: #ffebee;
            padding: 10px;
            border-left: 4px solid #f44336;
        }
        .genuine-review {
            background-color: #e8f5e9;
            padding: 10px;
            border-left: 4px solid #4caf50;
        }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if "backend_healthy" not in st.session_state:
        st.session_state.backend_healthy = None
    if "last_health_check" not in st.session_state:
        st.session_state.last_health_check = None
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "threshold": 0.5,
            "use_bert": False,
            "ensemble_weights": "0.4, 0.35, 0.25",
            "send_emails": False,
        }
    if "api_url" not in st.session_state:
        # Try to get from secrets, otherwise use default
        try:
            if "API_URL" in st.secrets:
                st.session_state.api_url = st.secrets["API_URL"]
            else:
                st.session_state.api_url = "http://localhost:8000/api"
        except Exception:
            st.session_state.api_url = "http://localhost:8000/api"


def check_backend_health():
    """Check backend health and update session state."""
    try:
        client = get_client()
        health = health_check_sync()
        is_healthy = safe_get(health, "status") == "ok" or safe_get(health, "status") == "healthy"
        st.session_state.backend_healthy = is_healthy
        st.session_state.last_health_check = datetime.now()
        return is_healthy
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        st.session_state.backend_healthy = False
        st.session_state.last_health_check = datetime.now()
        return False


init_session_state()

def get_dashboard_stats():
    """Fetch dashboard statistics."""
    try:
        client = get_client()
        from app.api_client import get_sync
        response = get_sync("/admin/dashboard/stats")
        return response
    except APIError as e:
        error_msg = map_api_error_to_user_message(e)
        st.error(error_msg)
        logger.error(f"Failed to fetch dashboard stats: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error fetching statistics: {str(e)}")
        logger.error(f"Unexpected error: {e}")
        return None


def get_flagged_reviews(page: int = 1, limit: int = 20):
    """Fetch flagged reviews with pagination."""
    try:
        client = get_client()
        from app.api_client import get_sync
        response = get_sync("/admin/flagged-reviews", params={"page": page, "limit": limit})
        return response if isinstance(response, list) else response.get("reviews", [])
    except APIError as e:
        error_msg = map_api_error_to_user_message(e)
        st.error(error_msg)
        logger.error(f"Failed to fetch flagged reviews: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error fetching flagged reviews: {str(e)}")
        logger.error(f"Unexpected error: {e}")
        return []


def override_review(review_id: str):
    """Override a review (mark as genuine)."""
    try:
        from app.api_client import post_sync
        response = post_sync(f"/admin/reviews/{review_id}/override")
        return True, "Review overridden successfully"
    except APIError as e:
        error_msg = map_api_error_to_user_message(e)
        logger.error(f"Failed to override review {review_id}: {e}")
        return False, error_msg
    except Exception as e:
        logger.error(f"Unexpected error overriding review: {e}")
        return False, f"Unexpected error: {str(e)}"


def delete_review(review_id: str):
    """Request deletion of a review."""
    try:
        from app.api_client import post_sync
        response = post_sync(f"/admin/reviews/{review_id}/delete")
        return True, "Deletion request submitted successfully"
    except APIError as e:
        error_msg = map_api_error_to_user_message(e)
        logger.error(f"Failed to delete review {review_id}: {e}")
        return False, error_msg
    except Exception as e:
        logger.error(f"Unexpected error deleting review: {e}")
        return False, f"Unexpected error: {str(e)}"


def main():
    """Main dashboard function."""
    
    st.title("🔍 Fake Review Detection System")
    st.markdown("---")
    
    # Check backend health on first load or when retry is requested
    if st.session_state.backend_healthy is None:
        with st.spinner("Checking backend connection..."):
            check_backend_health()
    
    # Show health status banner
    def retry_health_check():
        check_backend_health()
        st.rerun()
    
    render_health_status(
        st.session_state.backend_healthy,
        on_retry=retry_health_check
    )
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Flagged Reviews", "Manual Check", "Batch Analysis", "Settings"]
        )
    
    # Dashboard Page
    if page == "Dashboard":
        col1, col2, col3 = st.columns(3)
        
        stats = get_dashboard_stats()
        
        if stats:
            with col1:
                st.metric(
                    "Total Reviews",
                    stats['total_reviews'],
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Fake Reviews",
                    stats['fake_reviews'],
                    delta=f"{stats['fake_percentage']:.1f}%",
                    delta_color="inverse"
                )
            
            with col3:
                st.metric(
                    "Trust Score",
                    f"{stats['average_trust_score']:.2f}",
                    delta="Average"
                )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if stats:
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Genuine', 'Fake'],
                        y=[stats['genuine_reviews'], stats['fake_reviews']],
                        marker_color=['#4caf50', '#f44336']
                    )
                ])
                fig.update_layout(title="Review Classification", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if stats:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=['Genuine', 'Fake', 'Flagged', 'Removed'],
                        values=[
                            stats['genuine_reviews'],
                            stats['fake_reviews'],
                            stats['flagged_reviews'],
                            stats['removed_reviews']
                        ],
                        marker_colors=['#4caf50', '#f44336', '#ff9800', '#9c27b0']
                    )
                ])
                fig.update_layout(title="Review Status Distribution", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Flagged Reviews Page
    elif page == "Flagged Reviews":
        st.header("Flagged Reviews")
        
        # Initialize pagination in session state
        if "flagged_page" not in st.session_state:
            st.session_state.flagged_page = 1
        
        with render_loading_spinner("Loading flagged reviews..."):
            flagged = get_flagged_reviews(page=st.session_state.flagged_page, limit=20)
        
        if flagged:
            # Handler functions for actions
            def handle_override(review_id: str):
                # Set pending state
                st.session_state[f"pending_{review_id}"] = True
                
                # Call API
                success, message = override_review(review_id)
                
                # Clear pending state
                st.session_state[f"pending_{review_id}"] = False
                
                if success:
                    render_success_message(message)
                    # Refresh reviews
                    st.rerun()
                else:
                    st.error(message)
            
            def handle_delete(review_id: str):
                # Set pending state
                st.session_state[f"pending_{review_id}"] = True
                
                # Call API
                success, message = delete_review(review_id)
                
                # Clear pending state
                st.session_state[f"pending_{review_id}"] = False
                
                if success:
                    render_success_message(message)
                    # Refresh reviews
                    st.rerun()
                else:
                    st.error(message)
            
            # Render each review
            for review in flagged:
                render_review_card(
                    review,
                    on_override=handle_override,
                    on_delete=handle_delete
                )
        else:
            render_info_message("No flagged reviews", icon="✅")
    
    # Manual Check Page
    elif page == "Manual Check":
        st.header("Manual Review Check")
        
        col1, col2 = st.columns(2)
        
        with col1:
            review_text = st.text_area("Review Text", height=150)
            rating = st.slider("Rating", 1.0, 5.0, 3.0)
        
        with col2:
            product_name = st.text_input("Product Name")
            platform = st.selectbox("Platform", ["amazon", "flipkart", "other"])
        
        if st.button("Check Review", type="primary"):
            # Validate inputs
            is_valid, error_msg = validate_review_input(review_text, rating, product_name)
            
            if not is_valid:
                render_warning_message(error_msg)
            else:
                with render_loading_spinner("Analyzing review..."):
                    try:
                        from app.api_client import post_sync
                        
                        result = post_sync(
                            "/reviews/check",
                            json={
                                "text": review_text,
                                "rating": rating,
                                "product_name": product_name,
                                "platform": platform
                            },
                            timeout=30.0
                        )
                        
                        # Validate response structure
                        required_keys = ["is_fake", "fake_probability", "confidence", "reasons"]
                        is_valid_response, error = check_response_structure(result, required_keys)
                        
                        if not is_valid_response:
                            st.error(f"Invalid response from backend: {error}")
                        else:
                            # Store result in session state
                            st.session_state["last_manual_check"] = result
                            
                            # Display result
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if result["is_fake"]:
                                    st.error(f"🚨 LIKELY FAKE ({format_percentage(result['fake_probability'])})")
                                else:
                                    st.success(f"✓ LIKELY GENUINE ({format_percentage(1 - result['fake_probability'])})")
                            
                            with col2:
                                st.metric("Confidence", format_confidence(result["confidence"]))
                            
                            # Reasons
                            st.markdown("**Reasons:**")
                            for reason in result["reasons"]:
                                st.markdown(f"- {reason}")
                            
                            # Model probabilities
                            if "model_probabilities" in result:
                                st.markdown("**Model Predictions:**")
                                models_col1, models_col2, models_col3 = st.columns(3)
                                
                                model_probs = result["model_probabilities"]
                                
                                with models_col1:
                                    rf_prob = safe_get(model_probs, "random_forest", default=0)
                                    st.metric("Random Forest", format_percentage(rf_prob))
                                
                                with models_col2:
                                    xgb_prob = safe_get(model_probs, "xgboost", default=0)
                                    st.metric("XGBoost", format_percentage(xgb_prob))
                                
                                with models_col3:
                                    svm_prob = safe_get(model_probs, "svm", default=0)
                                    st.metric("SVM", format_percentage(svm_prob))
                    
                    except APIError as e:
                        error_msg = map_api_error_to_user_message(e)
                        render_error_banner(error_msg, error_detail=str(e.detail) if e.detail else None)
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                        logger.error(f"Manual check error: {e}")
    
    # Batch Analysis Page
    elif page == "Batch Analysis":
        st.header("Batch Review Analysis")
        
        st.info("📋 Upload a CSV file with columns: **text** (required), **rating** (required), **product_id**, **platform**, **product_name** (optional)")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type="csv"
        )
        
        if uploaded_file is not None:
            # Show file info
            st.write(f"**File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            # Validate CSV
            is_valid, error_msg, df = validate_csv_file(uploaded_file)
            
            if not is_valid:
                render_warning_message(error_msg)
            else:
                st.success(f"✅ File validated: {len(df)} reviews ready to analyze")
                
                # Show preview
                with st.expander("📊 Preview data (first 5 rows)"):
                    st.dataframe(df.head())
                
                if st.button("Analyze Batch", type="primary"):
                    with render_loading_spinner("Processing batch... This may take a moment."):
                        try:
                            from app.api_client import post_sync, UPLOAD_TIMEOUT
                            import io
                            
                            # Reset file pointer
                            uploaded_file.seek(0)
                            
                            # Prepare file for upload
                            files = {
                                "file": (uploaded_file.name, uploaded_file, "text/csv")
                            }
                            
                            # Send to backend
                            result = post_sync(
                                "/reviews/batch",
                                files=files,
                                timeout=UPLOAD_TIMEOUT
                            )
                            
                            # Validate response
                            required_keys = ["total_reviews", "fake_count", "genuine_count", "results"]
                            is_valid_response, error = check_response_structure(result, required_keys)
                            
                            if not is_valid_response:
                                st.error(f"Invalid response from backend: {error}")
                            else:
                                # Display statistics
                                st.markdown("### 📊 Analysis Results")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                total = result["total_reviews"]
                                fake_count = result["fake_count"]
                                genuine_count = result["genuine_count"]
                                
                                with col1:
                                    st.metric("Total Reviews", total)
                                with col2:
                                    st.metric(
                                        "Fake Reviews",
                                        fake_count,
                                        delta=format_percentage(fake_count / total if total > 0 else 0),
                                        delta_color="inverse"
                                    )
                                with col3:
                                    st.metric("Genuine Reviews", genuine_count)
                                with col4:
                                    processing_time = safe_get(result, "processing_time", default="N/A")
                                    st.metric("Processing Time", processing_time)
                                
                                # Results table
                                st.markdown("### 📋 Detailed Results")
                                results_df = parse_batch_results(result)
                                
                                if results_df is not None:
                                    st.dataframe(results_df, use_container_width=True)
                                    
                                    # Download button
                                    csv_buffer = io.StringIO()
                                    results_df.to_csv(csv_buffer, index=False)
                                    csv_bytes = csv_buffer.getvalue().encode()
                                    
                                    render_download_button(
                                        label="📥 Download Annotated Results",
                                        data=csv_bytes,
                                        file_name=f"annotated_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv",
                                        help_text="Download results with fake detection analysis"
                                    )
                                    
                                    # Store in session state
                                    st.session_state["last_batch_results"] = result
                                else:
                                    st.error("Failed to parse batch results")
                        
                        except APIError as e:
                            error_msg = map_api_error_to_user_message(e)
                            render_error_banner(
                                error_msg,
                                error_detail=str(e.detail) if e.detail else None
                            )
                        except Exception as e:
                            st.error(f"Unexpected error: {str(e)}")
                            logger.error(f"Batch analysis error: {e}")
    
    # Settings Page
    elif page == "Settings":
        st.header("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Classification Threshold")
            threshold = st.slider(
                "Fake probability threshold (0-1)",
                0.0, 1.0,
                st.session_state.settings["threshold"],
                0.05
            )
            st.info(f"Reviews with probability > {threshold} will be classified as fake")
            
            st.subheader("Model Settings")
            use_bert = st.checkbox(
                "Enable BERT embeddings",
                value=st.session_state.settings["use_bert"]
            )
            if use_bert:
                st.warning("⚠️ BERT embeddings require significant memory and may not be available on all deployments")
            
            ensemble_weights = st.text_input(
                "Ensemble weights (RF, XGBoost, SVM)",
                st.session_state.settings["ensemble_weights"]
            )
        
        with col2:
            st.subheader("API Configuration")
            api_url = st.text_input(
                "API Base URL",
                st.session_state.api_url
            )
            
            st.subheader("Email Notifications")
            send_emails = st.checkbox(
                "Send email notifications",
                value=st.session_state.settings["send_emails"]
            )
            
            if send_emails:
                admin_email = st.text_input(
                    "Admin email",
                    st.session_state.settings.get("admin_email", "")
                )
                notification_frequency = st.selectbox(
                    "Notification frequency",
                    ["Hourly", "Daily", "Weekly"],
                    index=["Hourly", "Daily", "Weekly"].index(
                        st.session_state.settings.get("notification_frequency", "Daily")
                    )
                )
        
        if st.button("Save Settings", type="primary"):
            # Update session state
            st.session_state.settings.update({
                "threshold": threshold,
                "use_bert": use_bert,
                "ensemble_weights": ensemble_weights,
                "send_emails": send_emails,
            })
            
            if send_emails:
                st.session_state.settings.update({
                    "admin_email": admin_email,
                    "notification_frequency": notification_frequency,
                })
            
            # Update API URL if changed
            if api_url != st.session_state.api_url:
                st.session_state.api_url = api_url
                # Reset client to pick up new URL
                get_client()._base_url = None
            
            # Try to persist to backend
            try:
                from app.api_client import post_sync
                
                settings_payload = {
                    "threshold": threshold,
                    "use_bert": use_bert,
                    "ensemble_weights": ensemble_weights,
                    "send_emails": send_emails,
                }
                
                if send_emails:
                    settings_payload.update({
                        "admin_email": admin_email,
                        "notification_frequency": notification_frequency,
                    })
                
                post_sync("/admin/settings", json=settings_payload, timeout=10.0)
                
                render_success_message(
                    f"Settings saved successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            except APIError as e:
                # Settings saved locally even if backend fails
                error_msg = map_api_error_to_user_message(e)
                render_warning_message(
                    f"Settings saved locally, but failed to sync with backend: {error_msg}"
                )
            except Exception as e:
                render_warning_message(
                    f"Settings saved locally, but failed to sync with backend: {str(e)}"
                )


if __name__ == "__main__":
    main()
