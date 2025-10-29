"""
Quick validation script to test the new API client and utilities.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 60)
print("Dashboard Refactoring - Module Validation")
print("=" * 60)

# Test 1: Import API Client
print("\n1. Testing API Client import...")
try:
    from app.api_client import APIClient, APIError, get_client, health_check_sync
    print("   ✅ API Client imported successfully")
    
    # Create a client and test base URL
    client = get_client()
    client.set_base_url("http://test-api.example.com/api")
    assert client.get_base_url() == "http://test-api.example.com/api"
    print("   ✅ API Client base URL configuration works")
except Exception as e:
    print(f"   ❌ API Client import failed: {e}")

# Test 2: Import Utils
print("\n2. Testing Utils import...")
try:
    from app.utils import (
        validate_csv_file,
        validate_review_input,
        map_api_error_to_user_message,
        format_percentage,
        safe_get,
    )
    print("   ✅ Utils imported successfully")
    
    # Test format_percentage
    assert format_percentage(0.5) == "50.0%"
    print("   ✅ format_percentage works")
    
    # Test safe_get
    test_data = {"a": {"b": {"c": 123}}}
    assert safe_get(test_data, "a", "b", "c") == 123
    print("   ✅ safe_get works")
    
    # Test validate_review_input
    is_valid, error = validate_review_input("This is a test review", 4.5)
    assert is_valid is True
    print("   ✅ validate_review_input works")
except Exception as e:
    print(f"   ❌ Utils import failed: {e}")

# Test 3: Import Components
print("\n3. Testing Dashboard Components import...")
try:
    from dashboard.components import (
        render_review_card,
        render_error_banner,
        render_health_status,
    )
    print("   ✅ Dashboard Components imported successfully")
except Exception as e:
    print(f"   ❌ Dashboard Components import failed: {e}")

# Test 4: Check required packages
print("\n4. Checking required packages...")
try:
    import httpx
    print(f"   ✅ httpx {httpx.__version__}")
except ImportError:
    print("   ❌ httpx not installed")

try:
    import tenacity
    print("   ✅ tenacity installed")
except ImportError:
    print("   ❌ tenacity not installed")

try:
    import nest_asyncio
    print("   ✅ nest_asyncio installed")
except ImportError:
    print("   ❌ nest_asyncio not installed")

try:
    import streamlit as st
    print(f"   ✅ streamlit {st.__version__}")
except ImportError:
    print("   ⚠️  streamlit not installed (required for dashboard)")

try:
    import pandas as pd
    print(f"   ✅ pandas {pd.__version__}")
except ImportError:
    print("   ❌ pandas not installed")

try:
    import plotly
    print(f"   ✅ plotly {plotly.__version__}")
except ImportError:
    print("   ❌ plotly not installed")

# Summary
print("\n" + "=" * 60)
print("Validation Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Start your FastAPI backend: uvicorn app.main:app --reload")
print("2. Run Streamlit dashboard: streamlit run dashboard/app.py")
print("3. Configure .streamlit/secrets.toml with your API_URL")
print("\nFor tests, run: pytest tests/ -v")
print("=" * 60)
