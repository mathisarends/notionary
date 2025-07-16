import asyncio
import os
from abc import ABC
from enum import Enum
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv
from notionary.util import LoggingMixin, singleton

load_dotenv()


class HttpMethod(Enum):
    """
    Enumeration of supported HTTP methods for API requests.
    """

    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class BaseNotionClient(LoggingMixin, ABC):
    """
    Base client for Notion API operations.
    Handles connection management and generic HTTP requests.
    """

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        self.token = token or self._find_token()
        if not self.token:
            raise ValueError("Notion API token is required")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

        self.client: Optional[httpx.AsyncClient] = None
        self.timeout = timeout
        self._is_initialized = False

    def __del__(self):
        """Auto-cleanup when client is destroyed."""
        if not hasattr(self, "client") or not self.client:
            return

        try:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                self.logger.warning(
                    "Event loop not running, could not auto-close NotionClient"
                )
                return

            loop.create_task(self.close())
            self.logger.debug("Created cleanup task for NotionClient")
        except RuntimeError:
            self.logger.warning("No event loop available for auto-closing NotionClient")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def ensure_initialized(self) -> None:
        """
        Ensures the HTTP client is initialized.
        """
        if not self._is_initialized or not self.client:
            self.client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
            self._is_initialized = True
            self.logger.debug("NotionClient initialized")

    async def close(self) -> None:
        """
        Closes the HTTP client and releases resources.
        """
        if not hasattr(self, "client") or not self.client:
            return

        await self.client.aclose()
        self.client = None
        self._is_initialized = False
        self.logger.debug("NotionClient closed")

    async def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Sends a GET request to the specified Notion API endpoint.

        Args:
            endpoint: The API endpoint (without base URL)
        """
        return await self._make_request(HttpMethod.GET, endpoint)

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a POST request to the specified Notion API endpoint.

        Args:
            endpoint: The API endpoint (without base URL)
            data: Request body data
        """
        return await self._make_request(HttpMethod.POST, endpoint, data)

    async def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a PATCH request to the specified Notion API endpoint.

        Args:
            endpoint: The API endpoint (without base URL)
            data: Request body data
        """
        return await self._make_request(HttpMethod.PATCH, endpoint, data)

    async def delete(self, endpoint: str) -> bool:
        """
        Sends a DELETE request to the specified Notion API endpoint.

        Args:
            endpoint: The API endpoint (without base URL)
        """
        result = await self._make_request(HttpMethod.DELETE, endpoint)
        return result is not None

    async def _make_request(
        self,
        method: Union[HttpMethod, str],
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Executes an HTTP request and returns the data or None on error.

        Args:
            method: HTTP method to use
            endpoint: API endpoint
            data: Request body data (for POST/PATCH)
        """
        await self.ensure_initialized()

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        method_str = (
            method.value if isinstance(method, HttpMethod) else str(method).lower()
        )

        try:
            self.logger.debug("Sending %s request to %s", method_str.upper(), url)

            if (
                method_str in [HttpMethod.POST.value, HttpMethod.PATCH.value]
                and data is not None
            ):
                response: httpx.Response = await getattr(self.client, method_str)(
                    url, json=data
                )
            else:
                response: httpx.Response = await getattr(self.client, method_str)(url)

            response.raise_for_status()
            result_data = response.json()
            self.logger.debug("Request successful: %s", url)
            return result_data

        except httpx.HTTPStatusError as e:
            error_msg = (
                f"HTTP status error: {e.response.status_code} - {e.response.text}"
            )
            self.logger.error("Request failed (%s): %s", url, error_msg)
            return None

        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            self.logger.error("Request error (%s): %s", url, error_msg)
            return None

    def _find_token(self) -> Optional[str]:
        """
        Finds the Notion API token from environment variables.
        """
        token = next(
            (
                os.getenv(var)
                for var in ("NOTION_SECRET", "NOTION_API_KEY", "NOTION_TOKEN")
                if os.getenv(var)
            ),
            None,
        )
        if token:
            self.logger.debug("Found token in environment variable.")
            return token
        self.logger.warning("No Notion API token found in environment variables")
        return None
