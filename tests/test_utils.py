"""
Unit tests for utility functions module.

Tests CSV validation, error mapping, and response checking.
"""
import pytest
import pandas as pd
import io
from unittest.mock import Mock
from app.utils import (
    validate_csv_file,
    validate_review_input,
    map_api_error_to_user_message,
    check_response_structure,
    format_percentage,
    format_confidence,
    safe_get,
    parse_batch_results,
    truncate_text,
    MAX_UPLOAD_SIZE_BYTES,
)
from app.api_client import APIError


def create_csv_file(content: str, filename: str = "test.csv"):
    """Helper to create a mock CSV file."""
    csv_buffer = io.BytesIO(content.encode())
    csv_buffer.name = filename
    csv_buffer.size = len(content)
    csv_buffer.seek(0)
    return csv_buffer


def test_validate_csv_file_success():
    """Test successful CSV validation."""
    csv_content = "text,rating,product_id\nGreat product!,5,P123\nBad quality,1,P456"
    csv_file = create_csv_file(csv_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is True
    assert error_msg is None
    assert df is not None
    assert len(df) == 2
    assert "text" in df.columns
    assert "rating" in df.columns


def test_validate_csv_file_missing_columns():
    """Test CSV validation with missing required columns."""
    csv_content = "review,score\nGreat product!,5"
    csv_file = create_csv_file(csv_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is False
    assert "Missing required columns" in error_msg
    assert df is None


def test_validate_csv_file_empty():
    """Test CSV validation with empty file."""
    csv_content = "text,rating\n"
    csv_file = create_csv_file(csv_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_content)
    
    assert is_valid is False
    assert "empty" in error_msg.lower()


def test_validate_csv_file_invalid_rating():
    """Test CSV validation with invalid rating values."""
    csv_content = "text,rating\nGreat product!,invalid"
    csv_file = create_csv_file(csv_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is False
    assert "rating" in error_msg.lower()


def test_validate_csv_file_rating_out_of_range():
    """Test CSV validation with rating out of valid range."""
    csv_content = "text,rating\nGreat product!,10"
    csv_file = create_csv_file(csv_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is False
    assert "1 and 5" in error_msg


def test_validate_csv_file_too_large():
    """Test CSV validation with file exceeding size limit."""
    # Create a very large CSV content
    large_content = "text,rating\n" + ("A" * (MAX_UPLOAD_SIZE_BYTES + 1000))
    csv_file = create_csv_file(large_content)
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is False
    assert "too large" in error_msg.lower()


def test_validate_csv_file_wrong_extension():
    """Test CSV validation with wrong file extension."""
    csv_content = "text,rating\nGreat,5"
    csv_file = create_csv_file(csv_content, filename="test.txt")
    
    is_valid, error_msg, df = validate_csv_file(csv_file)
    
    assert is_valid is False
    assert ".csv" in error_msg.lower()


def test_validate_review_input_success():
    """Test successful review input validation."""
    is_valid, error_msg = validate_review_input(
        text="This is a great product that I really enjoyed using!",
        rating=4.5,
        product_name="Test Product"
    )
    
    assert is_valid is True
    assert error_msg is None


def test_validate_review_input_empty_text():
    """Test review validation with empty text."""
    is_valid, error_msg = validate_review_input(text="", rating=4.0)
    
    assert is_valid is False
    assert "empty" in error_msg.lower()


def test_validate_review_input_text_too_short():
    """Test review validation with text too short."""
    is_valid, error_msg = validate_review_input(text="Short", rating=4.0)
    
    assert is_valid is False
    assert "too short" in error_msg.lower()


def test_validate_review_input_text_too_long():
    """Test review validation with text too long."""
    long_text = "A" * 6000
    is_valid, error_msg = validate_review_input(text=long_text, rating=4.0)
    
    assert is_valid is False
    assert "too long" in error_msg.lower()


def test_validate_review_input_invalid_rating():
    """Test review validation with invalid rating."""
    is_valid, error_msg = validate_review_input(
        text="Good product review",
        rating=10.0
    )
    
    assert is_valid is False
    assert "between 1 and 5" in error_msg.lower()


def test_map_api_error_404():
    """Test error mapping for 404 status."""
    error = APIError("Not found", status_code=404, detail="Resource not found")
    
    message = map_api_error_to_user_message(error)
    
    assert "not found" in message.lower()
    assert "⚠️" in message


def test_map_api_error_500():
    """Test error mapping for 500 status."""
    error = APIError("Server error", status_code=500, detail="Internal error")
    
    message = map_api_error_to_user_message(error)
    
    assert "server error" in message.lower()
    assert "🔥" in message


def test_map_api_error_timeout():
    """Test error mapping for timeout."""
    error = APIError("Request timed out after 10s", status_code=None)
    
    message = map_api_error_to_user_message(error)
    
    assert "timeout" in message.lower() or "timed out" in message.lower()
    assert "⏱️" in message


def test_map_api_error_network():
    """Test error mapping for network error."""
    error = APIError("Network error - could not connect", status_code=None)
    
    message = map_api_error_to_user_message(error)
    
    assert "connect" in message.lower() or "network" in message.lower()
    assert "🌐" in message


def test_check_response_structure_success():
    """Test successful response structure check."""
    response = {"status": "ok", "data": "test", "count": 5}
    required_keys = ["status", "data"]
    
    is_valid, error_msg = check_response_structure(response, required_keys)
    
    assert is_valid is True
    assert error_msg is None


def test_check_response_structure_missing_keys():
    """Test response structure check with missing keys."""
    response = {"status": "ok"}
    required_keys = ["status", "data", "count"]
    
    is_valid, error_msg = check_response_structure(response, required_keys)
    
    assert is_valid is False
    assert "Missing required keys" in error_msg
    assert "data" in error_msg
    assert "count" in error_msg


def test_check_response_structure_not_dict():
    """Test response structure check with non-dict response."""
    response = ["list", "of", "items"]
    required_keys = ["status"]
    
    is_valid, error_msg = check_response_structure(response, required_keys)
    
    assert is_valid is False
    assert "Expected dict" in error_msg


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.5) == "50.0%"
    assert format_percentage(0.123, decimals=2) == "12.30%"
    assert format_percentage(0.99, decimals=0) == "99%"


def test_format_confidence():
    """Test confidence formatting with emoji."""
    high = format_confidence(0.9)
    assert "🟢" in high
    assert "90.0%" in high
    
    medium = format_confidence(0.7)
    assert "🟡" in medium
    
    low = format_confidence(0.4)
    assert "🔴" in low


def test_safe_get_nested():
    """Test safe nested dictionary access."""
    data = {"a": {"b": {"c": 123}}}
    
    result = safe_get(data, "a", "b", "c", default=0)
    assert result == 123


def test_safe_get_missing_key():
    """Test safe get with missing key."""
    data = {"a": {"b": {}}}
    
    result = safe_get(data, "a", "b", "c", default="missing")
    assert result == "missing"


def test_safe_get_partial_path():
    """Test safe get with partial path."""
    data = {"a": None}
    
    result = safe_get(data, "a", "b", "c", default=0)
    assert result == 0


def test_parse_batch_results_success():
    """Test successful batch results parsing."""
    response = {
        "results": [
            {"text": "Review 1", "is_fake": True, "fake_probability": 0.8},
            {"text": "Review 2", "is_fake": False, "fake_probability": 0.3},
        ]
    }
    
    df = parse_batch_results(response)
    
    assert df is not None
    assert len(df) == 2
    assert "text" in df.columns


def test_parse_batch_results_missing_key():
    """Test batch results parsing with missing key."""
    response = {"data": "something else"}
    
    df = parse_batch_results(response)
    
    assert df is None


def test_truncate_text():
    """Test text truncation."""
    short_text = "Short"
    assert truncate_text(short_text, max_length=100) == "Short"
    
    long_text = "A" * 200
    truncated = truncate_text(long_text, max_length=50)
    assert len(truncated) == 50
    assert truncated.endswith("...")


def test_truncate_text_custom_suffix():
    """Test text truncation with custom suffix."""
    text = "A" * 100
    truncated = truncate_text(text, max_length=20, suffix="[...]")
    
    assert len(truncated) == 20
    assert truncated.endswith("[...]")
