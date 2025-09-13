import asyncio
import os
from enum import Enum
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

from notionary.http.exceptions import (
    NotionApiError,
    NotionAuthenticationError,
    NotionConnectionError,
    NotionPermissionError,
    NotionRateLimitError,
    NotionResourceNotFoundError,
    NotionServerError,
    NotionValidationError,
)
from notionary.page.page_models import NotionPageDto
from notionary.util import LoggingMixin

load_dotenv()


class HttpMethod(Enum):
    """
    Enumeration of supported HTTP methods for API requests.
    """

    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class NotionClient(LoggingMixin):
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
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

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

    async def get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Sends a GET request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.GET, endpoint, params=params)

    async def post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Sends a POST request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.POST, endpoint, data)

    async def patch(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Sends a PATCH request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.PATCH, endpoint, data)

    async def delete(self, endpoint: str) -> bool:
        """
        Sends a DELETE request to the specified Notion API endpoint.
        """
        result = await self._make_request(HttpMethod.DELETE, endpoint)
        return result is not None

    async def get_page(self, page_id: str) -> NotionPageDto:
        """
        Gets metadata for a Notion page by its ID.
        """
        response = await self.get(f"pages/{page_id}")
        return NotionPageDto.model_validate(response)

    async def _make_request(
        self,
        method: HttpMethod,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Executes an HTTP request and returns the data or None on error.

        Args:
            method: HTTP method to use
            endpoint: API endpoint
            data: Request body data (for POST/PATCH)
            params: Query parameters (for GET requests)
        """
        await self._ensure_initialized()

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            self.logger.debug("Sending %s request to %s", method.value.upper(), url)

            request_kwargs = {}

            # Add query parameters for GET requests
            if params:
                request_kwargs["params"] = params

            if (
                method.value in [HttpMethod.POST.value, HttpMethod.PATCH.value]
                and data is not None
            ):
                request_kwargs["json"] = data

            response: httpx.Response = await getattr(self.client, method.value)(
                url, **request_kwargs
            )

            response.raise_for_status()
            result_data = response.json()
            self.logger.debug("Request successful: %s", url)
            return result_data

        except httpx.HTTPStatusError as e:
            self._handle_http_status_error(e)
        except httpx.RequestError as e:
            raise NotionConnectionError(
                f"Failed to connect to Notion API: {str(e)}. "
                "Please check your internet connection and try again."
            )

    def _handle_http_status_error(self, e: httpx.HTTPStatusError) -> None:
        """
        Handles HTTP status errors by raising appropriate Notion exceptions.

        Args:
            e: The HTTPStatusError exception
        """
        status_code = e.response.status_code
        response_text = e.response.text

        # Map HTTP status codes to specific business exceptions
        if status_code == 401:
            raise NotionAuthenticationError(
                "Invalid or missing API key. Please check your Notion integration token.",
                status_code=status_code,
                response_text=response_text,
            )
        if status_code == 403:
            raise NotionPermissionError(
                "Insufficient permissions. Please check your integration settings at "
                "https://www.notion.so/profile/integrations and ensure the integration "
                "has access to the required pages/databases.",
                status_code=status_code,
                response_text=response_text,
            )
        if status_code == 404:
            raise NotionResourceNotFoundError(
                "The requested resource was not found. Please verify the page/database ID.",
                status_code=status_code,
                response_text=response_text,
            )
        if status_code == 400:
            raise NotionValidationError(
                f"Invalid request data. Please check your input parameters: {response_text}",
                status_code=status_code,
                response_text=response_text,
            )
        if status_code == 429:
            raise NotionRateLimitError(
                "Rate limit exceeded. Please wait before making more requests.",
                status_code=status_code,
                response_text=response_text,
            )
        if 500 <= status_code < 600:
            raise NotionServerError(
                "Notion API server error. Please try again later.",
                status_code=status_code,
                response_text=response_text,
            )

        raise NotionApiError(
            f"API request failed with status {status_code}: {response_text}",
            status_code=status_code,
            response_text=response_text,
        )

    def _find_token(self) -> Optional[str]:
        """
        Finds the Notion API token from environment variables.
        """
        token = next(
            (
                os.getenv(var)
                for var in ("NOTION_SECRET", "NOTION_INTEGRATION_KEY", "NOTION_TOKEN")
                if os.getenv(var)
            ),
            None,
        )
        if token:
            self.logger.debug("Found token in environment variable.")
            return token
        self.logger.warning("No Notion API token found in environment variables")
        return None

    async def _ensure_initialized(self) -> None:
        """
        Ensures the HTTP client is initialized.
        """
        if not self._is_initialized or not self.client:
            self.client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
            self._is_initialized = True
            self.logger.debug("NotionClient initialized")
