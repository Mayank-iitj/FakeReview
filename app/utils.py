"""
Utility functions for the dashboard application.

Provides:
- CSV validation
- Error message mapping
- Response checking
- Data formatting helpers
"""
import io
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from loguru import logger


# Configuration
MAX_UPLOAD_SIZE_MB = 50
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
REQUIRED_CSV_COLUMNS = ["text", "rating"]
OPTIONAL_CSV_COLUMNS = ["product_id", "platform", "product_name", "reviewer_name"]


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_csv_file(
    uploaded_file, required_columns: Optional[List[str]] = None
) -> Tuple[bool, Optional[str], Optional[pd.DataFrame]]:
    """
    Validate uploaded CSV file.

    Args:
        uploaded_file: Streamlit UploadedFile object
        required_columns: List of required column names (defaults to REQUIRED_CSV_COLUMNS)

    Returns:
        Tuple of (is_valid, error_message, dataframe)
        - is_valid: True if validation passed
        - error_message: Error description if validation failed, None otherwise
        - dataframe: Parsed DataFrame if valid, None otherwise
    """
    if required_columns is None:
        required_columns = REQUIRED_CSV_COLUMNS

    # Check file size
    try:
        file_size = uploaded_file.size
    except AttributeError:
        # Fallback for older Streamlit versions
        uploaded_file.seek(0, 2)  # Seek to end
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)  # Reset to beginning

    if file_size > MAX_UPLOAD_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        return (
            False,
            f"File too large ({size_mb:.1f}MB). Maximum size is {MAX_UPLOAD_SIZE_MB}MB.",
            None,
        )

    # Check file extension
    if not uploaded_file.name.lower().endswith(".csv"):
        return False, "File must be a CSV file (.csv extension).", None

    # Try to read CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        logger.error(f"Failed to parse CSV: {e}")
        return False, f"Failed to parse CSV file: {str(e)}", None

    # Check for empty file
    if df.empty:
        return False, "CSV file is empty.", None

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return (
            False,
            f"Missing required columns: {', '.join(missing_columns)}. "
            f"CSV must have: {', '.join(required_columns)}",
            None,
        )

    # Check for empty required columns
    for col in required_columns:
        if df[col].isna().all():
            return False, f"Required column '{col}' is empty.", None

    # Validate data types
    if "rating" in df.columns:
        try:
            df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
            if df["rating"].isna().any():
                return False, "Column 'rating' must contain numeric values.", None
            if not df["rating"].between(1, 5).all():
                return False, "Column 'rating' must have values between 1 and 5.", None
        except Exception as e:
            return False, f"Invalid rating values: {str(e)}", None

    # Check for reasonable row count
    if len(df) > 10000:
        return (
            False,
            f"Too many rows ({len(df)}). Maximum is 10,000 reviews per batch.",
            None,
        )

    logger.info(f"CSV validation passed: {len(df)} rows, {len(df.columns)} columns")
    return True, None, df


def validate_review_input(
    text: str, rating: float, product_name: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate manual review input.

    Args:
        text: Review text
        rating: Review rating (1-5)
        product_name: Optional product name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Review text cannot be empty."

    if len(text.strip()) < 10:
        return False, "Review text is too short (minimum 10 characters)."

    if len(text) > 5000:
        return False, "Review text is too long (maximum 5000 characters)."

    if not isinstance(rating, (int, float)):
        return False, "Rating must be a number."

    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5."

    if product_name is not None and len(product_name) > 200:
        return False, "Product name is too long (maximum 200 characters)."

    return True, None


def map_api_error_to_user_message(error: Exception) -> str:
    """
    Map API errors to user-friendly messages.

    Args:
        error: Exception from API call

    Returns:
        User-friendly error message
    """
    from app.api_client import APIError

    if isinstance(error, APIError):
        if error.status_code == 404:
            return "⚠️ The requested resource was not found. Please check the endpoint configuration."
        elif error.status_code == 400:
            detail = error.detail if isinstance(error.detail, str) else str(error.detail)
            return f"⚠️ Invalid request: {detail}"
        elif error.status_code == 401:
            return "🔒 Authentication required. Please check your API credentials."
        elif error.status_code == 403:
            return "🚫 Access denied. You don't have permission to perform this action."
        elif error.status_code == 429:
            return "⏱️ Too many requests. Please wait a moment and try again."
        elif error.status_code and 500 <= error.status_code < 600:
            return "🔥 Backend server error. Please try again later or contact support."
        elif error.status_code is None:
            if "timeout" in error.message.lower():
                return "⏱️ Request timed out. The server might be busy. Please try again."
            elif "network" in error.message.lower() or "connect" in error.message.lower():
                return "🌐 Cannot connect to the backend. Please check your internet connection and backend URL."
            elif "retry" in error.message.lower():
                return "❌ Request failed after multiple attempts. The backend might be unavailable."
        return f"❌ API Error: {error.message}"
    
    # Generic exception
    return f"❌ Unexpected error: {str(error)}"


def check_response_structure(
    response: Any, required_keys: List[str]
) -> Tuple[bool, Optional[str]]:
    """
    Check if API response has required structure.

    Args:
        response: API response (should be dict)
        required_keys: List of required keys in response

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(response, dict):
        return False, f"Expected dict response, got {type(response).__name__}"

    missing_keys = [key for key in required_keys if key not in response]
    if missing_keys:
        return False, f"Missing required keys in response: {', '.join(missing_keys)}"

    return True, None


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal value as percentage.

    Args:
        value: Decimal value (0-1)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_confidence(confidence: float) -> str:
    """
    Format confidence value with emoji indicator.

    Args:
        confidence: Confidence value (0-1)

    Returns:
        Formatted confidence string with emoji
    """
    emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
    return f"{emoji} {format_percentage(confidence)}"


def safe_get(data: Dict[str, Any], *keys, default=None) -> Any:
    """
    Safely get nested dictionary value.

    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key path not found

    Returns:
        Value at key path or default

    Example:
        safe_get({"a": {"b": {"c": 1}}}, "a", "b", "c", default=0)  # Returns 1
        safe_get({"a": {"b": {}}}, "a", "b", "c", default=0)  # Returns 0
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def prepare_csv_for_upload(df: pd.DataFrame) -> io.BytesIO:
    """
    Prepare DataFrame as CSV bytes for upload.

    Args:
        df: DataFrame to convert

    Returns:
        BytesIO object containing CSV data
    """
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def parse_batch_results(response: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    Parse batch analysis results into DataFrame.

    Args:
        response: API response from batch analysis

    Returns:
        DataFrame with results or None if parsing fails
    """
    try:
        if "results" in response:
            results_df = pd.DataFrame(response["results"])
            return results_df
        return None
    except Exception as e:
        logger.error(f"Failed to parse batch results: {e}")
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
