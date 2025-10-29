"""
Centralized async API client for dashboard backend communication.

Features:
- Async HTTP client using httpx
- Configurable timeouts
- Automatic retry with exponential backoff (3 attempts)
- Reads base URL from st.secrets or st.session_state
- Comprehensive error handling and mapping
"""
import asyncio
from typing import Any, Dict, Optional, Union
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)
from loguru import logger

# Default configuration
DEFAULT_TIMEOUT = 10.0
UPLOAD_TIMEOUT = 120.0
DEFAULT_BASE_URL = "http://localhost:8000/api"


class APIError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, detail: Any = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class APIClient:
    """Async API client with retry logic and error handling."""

    def __init__(self):
        self._base_url: Optional[str] = None

    def get_base_url(self) -> str:
        """
        Get API base URL from st.secrets, st.session_state, or default.
        
        Priority:
        1. st.secrets["API_URL"]
        2. st.session_state["api_url"]
        3. DEFAULT_BASE_URL
        """
        if self._base_url:
            return self._base_url

        try:
            import streamlit as st

            # Try secrets first (production)
            if hasattr(st, "secrets") and "API_URL" in st.secrets:
                self._base_url = st.secrets["API_URL"]
                logger.info(f"Using API URL from secrets: {self._base_url}")
                return self._base_url

            # Try session state (local dev override)
            if "api_url" in st.session_state:
                self._base_url = st.session_state["api_url"]
                logger.info(f"Using API URL from session_state: {self._base_url}")
                return self._base_url

        except Exception as e:
            logger.warning(f"Could not read Streamlit secrets/session_state: {e}")

        # Fallback to default
        self._base_url = DEFAULT_BASE_URL
        logger.info(f"Using default API URL: {self._base_url}")
        return self._base_url

    def set_base_url(self, url: str):
        """Manually set base URL (useful for testing)."""
        self._base_url = url
        logger.info(f"API base URL set to: {url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.ReadTimeout)),
        reraise=True,
    )
    async def _do_request(
        self,
        method: str,
        path: str,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Execute HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for httpx.request
            
        Returns:
            Response data (JSON dict, text, or bytes)
            
        Raises:
            APIError: On HTTP errors or invalid responses
        """
        base_url = self.get_base_url()
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        logger.debug(f"{method} {url} (timeout={timeout}s)")

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.request(method, url, **kwargs)

                # Log response
                logger.debug(
                    f"{method} {url} -> {response.status_code} "
                    f"({response.elapsed.total_seconds():.2f}s)"
                )

                # Check for HTTP errors
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    # Try to parse error detail from response
                    try:
                        error_detail = response.json()
                    except Exception:
                        error_detail = response.text

                    logger.error(
                        f"HTTP {response.status_code} error for {url}: {error_detail}"
                    )
                    raise APIError(
                        message=f"HTTP {response.status_code} error",
                        status_code=response.status_code,
                        detail=error_detail,
                    ) from exc

                # Parse response based on content type
                content_type = response.headers.get("content-type", "").lower()

                if "application/json" in content_type:
                    return response.json()
                elif "text/" in content_type:
                    return response.text
                else:
                    return response.content

        except httpx.TimeoutException as exc:
            logger.error(f"Request timeout for {url}")
            raise APIError(
                message=f"Request timed out after {timeout}s",
                status_code=None,
                detail=str(exc),
            ) from exc

        except httpx.TransportError as exc:
            logger.error(f"Transport error for {url}: {exc}")
            raise APIError(
                message="Network error - could not connect to backend",
                status_code=None,
                detail=str(exc),
            ) from exc

        except RetryError as exc:
            logger.error(f"All retry attempts exhausted for {url}")
            raise APIError(
                message="Request failed after 3 attempts",
                status_code=None,
                detail=str(exc),
            ) from exc

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Execute GET request.
        
        Args:
            path: API endpoint path
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response data
        """
        return await self._do_request("GET", path, params=params, timeout=timeout)

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Execute POST request.
        
        Args:
            path: API endpoint path
            json: JSON body
            data: Form data
            files: Files to upload
            timeout: Request timeout in seconds
            
        Returns:
            Response data
        """
        return await self._do_request(
            "POST", path, json=json, data=data, files=files, timeout=timeout
        )

    async def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Union[Dict[str, Any], str]:
        """Execute PUT request."""
        return await self._do_request("PUT", path, json=json, timeout=timeout)

    async def delete(
        self,
        path: str,
        timeout: Optional[float] = None,
    ) -> Union[Dict[str, Any], str]:
        """Execute DELETE request."""
        return await self._do_request("DELETE", path, timeout=timeout)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check backend health.
        
        Returns:
            Health status dict with 'status' key
            
        Raises:
            APIError: If health check fails
        """
        try:
            result = await self.get("/admin/health", timeout=5.0)
            if isinstance(result, dict):
                return result
            return {"status": "unknown", "detail": result}
        except APIError as exc:
            logger.error(f"Health check failed: {exc}")
            raise


# Global client instance
_client = APIClient()


def get_client() -> APIClient:
    """Get the global API client instance."""
    return _client


# Convenience functions for synchronous contexts
def run_async(coro):
    """
    Run async coroutine in sync context (for Streamlit).
    
    Args:
        coro: Async coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to use a different approach
            # This happens in Streamlit's async context
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(coro)


# Sync wrappers for convenience
def get_sync(path: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None):
    """Synchronous GET request."""
    return run_async(_client.get(path, params=params, timeout=timeout))


def post_sync(
    path: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
):
    """Synchronous POST request."""
    return run_async(_client.post(path, json=json, data=data, files=files, timeout=timeout))


def health_check_sync() -> Dict[str, Any]:
    """Synchronous health check."""
    return run_async(_client.health_check())
