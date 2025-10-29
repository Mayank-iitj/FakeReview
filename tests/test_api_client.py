"""
Unit tests for API client module.

Tests retry logic, timeout handling, and error mapping.
"""
import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from app.api_client import APIClient, APIError, run_async


@pytest.fixture
def api_client():
    """Create API client instance for testing."""
    client = APIClient()
    client.set_base_url("http://test-api.example.com/api")
    return client


@pytest.mark.asyncio
async def test_get_success(api_client):
    """Test successful GET request."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = await api_client.get("/test")
        
        assert result == {"status": "ok", "data": "test"}
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_post_success(api_client):
    """Test successful POST request."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 123, "created": True}
        mock_response.elapsed.total_seconds.return_value = 0.2
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = await api_client.post("/test", json={"name": "test"})
        
        assert result == {"id": 123, "created": True}


@pytest.mark.asyncio
async def test_http_404_error(api_client):
    """Test 404 error handling."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"detail": "Not found"}
        mock_response.text = "Not found"
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        def raise_http_error():
            raise httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        
        mock_response.raise_for_status = raise_http_error
        mock_request.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            await api_client.get("/nonexistent")
        
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_http_500_error(api_client):
    """Test 500 error handling."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Internal server error"
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        def raise_http_error():
            raise httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
        
        mock_response.raise_for_status = raise_http_error
        mock_request.return_value = mock_response
        
        with pytest.raises(APIError) as exc_info:
            await api_client.get("/error")
        
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_timeout_error(api_client):
    """Test timeout error handling."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_request.side_effect = httpx.TimeoutException("Request timeout")
        
        with pytest.raises(APIError) as exc_info:
            await api_client.get("/slow", timeout=1.0)
        
        assert "timed out" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_network_error(api_client):
    """Test network/connection error handling."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_request.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(APIError) as exc_info:
            await api_client.get("/unreachable")
        
        assert "network" in exc_info.value.message.lower() or "connect" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_retry_on_transport_error(api_client):
    """Test retry logic on transport errors."""
    with patch("httpx.AsyncClient.request") as mock_request:
        # Fail twice, then succeed
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.headers = {"content-type": "application/json"}
        mock_success_response.json.return_value = {"status": "ok"}
        mock_success_response.elapsed.total_seconds.return_value = 0.1
        mock_success_response.raise_for_status = Mock()
        
        mock_request.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.ConnectError("Connection failed"),
            mock_success_response,
        ]
        
        result = await api_client.get("/retry-test")
        
        # Should succeed after retries
        assert result == {"status": "ok"}
        assert mock_request.call_count == 3


@pytest.mark.asyncio
async def test_retry_exhausted(api_client):
    """Test when all retry attempts are exhausted."""
    with patch("httpx.AsyncClient.request") as mock_request:
        # Fail all attempts
        mock_request.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(APIError):
            await api_client.get("/always-fail")
        
        # Should attempt 3 times (initial + 2 retries based on tenacity config)
        assert mock_request.call_count == 3


@pytest.mark.asyncio
async def test_health_check_success(api_client):
    """Test successful health check."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "ok"}
        mock_response.elapsed.total_seconds.return_value = 0.05
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = await api_client.health_check()
        
        assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_health_check_failure(api_client):
    """Test failed health check."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_request.side_effect = httpx.ConnectError("Cannot connect")
        
        with pytest.raises(APIError):
            await api_client.health_check()


def test_get_base_url_default():
    """Test default base URL when no config available."""
    client = APIClient()
    
    # Mock streamlit not being available
    with patch("app.api_client.logger"):
        url = client.get_base_url()
        assert url == "http://localhost:8000/api"


def test_set_base_url():
    """Test manually setting base URL."""
    client = APIClient()
    client.set_base_url("https://prod-api.example.com/api")
    
    assert client.get_base_url() == "https://prod-api.example.com/api"


def test_run_async():
    """Test run_async helper for sync contexts."""
    async def async_func():
        return "test_result"
    
    result = run_async(async_func())
    assert result == "test_result"


@pytest.mark.asyncio
async def test_text_response(api_client):
    """Test handling of text/plain responses."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = await api_client.get("/text")
        
        assert result == "Plain text response"


@pytest.mark.asyncio
async def test_binary_response(api_client):
    """Test handling of binary responses."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/octet-stream"}
        mock_response.content = b"Binary data"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = await api_client.get("/binary")
        
        assert result == b"Binary data"


@pytest.mark.asyncio
async def test_file_upload(api_client):
    """Test file upload via POST."""
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"uploaded": True, "file_id": "abc123"}
        mock_response.elapsed.total_seconds.return_value = 1.5
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        files = {"file": ("test.csv", b"col1,col2\nval1,val2", "text/csv")}
        result = await api_client.post("/upload", files=files)
        
        assert result["uploaded"] is True
        assert result["file_id"] == "abc123"
