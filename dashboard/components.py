"""
Reusable UI components for the dashboard.

Provides consistent UI elements across pages.
"""
from typing import Any, Callable, Dict, Optional
import streamlit as st
from app.utils import format_percentage, truncate_text


def render_review_card(
    review: Dict[str, Any],
    on_override: Optional[Callable[[str], None]] = None,
    on_delete: Optional[Callable[[str], None]] = None,
    show_actions: bool = True,
) -> None:
    """
    Render a review card with optional action buttons.

    Args:
        review: Review data dict with keys:
            - id: Review ID
            - product_name: Product name
            - reviewer_name: Reviewer name
            - review_text: Review content
            - rating: Rating value
            - fake_probability: Probability of being fake (0-1)
            - flags: List of flag dicts with 'type' and 'reason'
        on_override: Callback function when Override button clicked (receives review_id)
        on_delete: Callback function when Delete button clicked (receives review_id)
        show_actions: Whether to show action buttons
    """
    review_id = review.get("id", "unknown")
    
    # Check if this review is in pending state
    pending_key = f"pending_{review_id}"
    is_pending = st.session_state.get(pending_key, False)
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Product and reviewer info
            product_name = review.get("product_name", "Unknown Product")
            reviewer_name = review.get("reviewer_name", "Anonymous")
            
            st.markdown(f"**{product_name}**")
            st.markdown(f"*By {reviewer_name}*")
            
            # Review text
            review_text = review.get("review_text", "")
            if len(review_text) > 200:
                with st.expander("📄 Review Text (click to expand)"):
                    st.write(review_text)
            else:
                st.write(review_text)
            
            # Flags
            flags = review.get("flags", [])
            if flags:
                st.markdown("**Flags:**")
                for flag in flags:
                    flag_type = flag.get("type", "Unknown")
                    flag_reason = flag.get("reason", "No reason provided")
                    st.warning(f"🚩 {flag_type}: {flag_reason}")
        
        with col2:
            # Metrics
            rating = review.get("rating", 0)
            fake_prob = review.get("fake_probability", 0)
            
            st.metric("Rating", f"⭐ {rating:.1f}")
            
            # Color-coded fake probability
            if fake_prob >= 0.7:
                st.metric("Fake Prob.", format_percentage(fake_prob), delta_color="inverse")
            else:
                st.metric("Fake Prob.", format_percentage(fake_prob))
        
        with col3:
            if show_actions:
                if is_pending:
                    st.info("⏳ Pending...")
                else:
                    # Override button
                    if on_override:
                        if st.button(
                            "✓ Override",
                            key=f"override_{review_id}",
                            help="Mark this review as genuine",
                            disabled=is_pending,
                        ):
                            on_override(review_id)
                    
                    # Delete button
                    if on_delete:
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{review_id}",
                            help="Request deletion of this review",
                            type="secondary",
                            disabled=is_pending,
                        ):
                            on_delete(review_id)
        
        st.divider()


def render_metric_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
) -> None:
    """
    Render a styled metric card.

    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta text
        delta_color: Color for delta ('normal', 'inverse', 'off')
        help_text: Optional help tooltip text
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text,
    )


def render_error_banner(
    message: str,
    error_detail: Optional[str] = None,
    show_retry: bool = False,
    on_retry: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render an error banner with optional details and retry button.

    Args:
        message: Main error message
        error_detail: Optional detailed error information
        show_retry: Whether to show retry button
        on_retry: Callback function when retry button clicked
    """
    st.error(message)
    
    if error_detail:
        with st.expander("🔍 Technical Details"):
            st.code(error_detail)
    
    if show_retry and on_retry:
        if st.button("🔄 Retry", key="error_retry"):
            on_retry()


def render_health_status(
    is_healthy: bool,
    on_retry: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render backend health status banner.

    Args:
        is_healthy: Whether backend is healthy
        on_retry: Callback function when retry button clicked
    """
    if not is_healthy:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.error(
                "🔴 **Backend Unavailable** - Some features may be limited. "
                "Please check your connection or contact support."
            )
        
        with col2:
            if on_retry:
                if st.button("🔄 Retry", key="health_retry"):
                    on_retry()


def render_loading_spinner(message: str = "Loading..."):
    """
    Render a loading spinner with message.

    Args:
        message: Loading message to display
    
    Returns:
        Context manager for st.spinner
    """
    return st.spinner(message)


def render_success_message(message: str, icon: str = "✅"):
    """
    Render a success message.

    Args:
        message: Success message
        icon: Emoji icon to display
    """
    st.success(f"{icon} {message}")


def render_info_message(message: str, icon: str = "ℹ️"):
    """
    Render an info message.

    Args:
        message: Info message
        icon: Emoji icon to display
    """
    st.info(f"{icon} {message}")


def render_warning_message(message: str, icon: str = "⚠️"):
    """
    Render a warning message.

    Args:
        message: Warning message
        icon: Emoji icon to display
    """
    st.warning(f"{icon} {message}")


def render_pagination_controls(
    current_page: int,
    total_pages: int,
    on_page_change: Callable[[int], None],
) -> None:
    """
    Render pagination controls.

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        on_page_change: Callback when page changes (receives new page number)
    """
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", disabled=current_page == 1):
            on_page_change(1)
    
    with col2:
        if st.button("◀️ Prev", disabled=current_page == 1):
            on_page_change(current_page - 1)
    
    with col3:
        st.markdown(
            f"<div style='text-align: center; padding-top: 8px;'>"
            f"Page {current_page} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    
    with col4:
        if st.button("Next ▶️", disabled=current_page >= total_pages):
            on_page_change(current_page + 1)
    
    with col5:
        if st.button("Last ⏭️", disabled=current_page >= total_pages):
            on_page_change(total_pages)


def render_progress_bar(
    progress: float,
    message: Optional[str] = None,
) -> None:
    """
    Render a progress bar.

    Args:
        progress: Progress value (0-1)
        message: Optional progress message
    """
    if message:
        st.write(message)
    st.progress(progress)


def render_download_button(
    label: str,
    data: bytes,
    file_name: str,
    mime: str = "text/csv",
    help_text: Optional[str] = None,
) -> bool:
    """
    Render a download button.

    Args:
        label: Button label
        data: Data to download (bytes)
        file_name: Name of downloaded file
        mime: MIME type
        help_text: Optional help tooltip

    Returns:
        True if button was clicked
    """
    return st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        help=help_text,
    )
