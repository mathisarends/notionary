import asyncio
import os
import weakref
from enum import Enum
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv
from notionary.util.logging_mixin import LoggingMixin


class HttpMethod(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class NotionClient(LoggingMixin):
    """Verbesserter Notion-Client mit automatischer Ressourcenverwaltung."""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    _instances = weakref.WeakSet()

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        load_dotenv()
        self.token = token or os.getenv("NOTION_SECRET", "")
        if not self.token:
            raise ValueError("Notion API token is required")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

        self.client = httpx.AsyncClient(headers=self.headers, timeout=timeout)

        self._instances.add(self)

    @classmethod
    async def close_all(cls):
        """
        Closes all active NotionClient instances and releases resources.
        """
        for instance in list(cls._instances):
            await instance.close()

    async def close(self):#
        """
        Closes the HTTP client for this instance and releases resources.
        """
        if hasattr(self, "client") and self.client:
            await self.client.aclose()
            self.client = None

    async def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Sends a GET request to the specified Notion API endpoint.

        Args:
            endpoint: The relative API path (e.g., 'databases/<id>').

        Returns:
            A dictionary with the response data, or None if the request failed.
        """
        return await self._make_request(HttpMethod.GET, endpoint)

    async def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches metadata for a Notion page by its ID.

        Args:
            page_id: The Notion page ID.

        Returns:
            A dictionary with the page data, or None if the request failed.
        """
        return await self.get(f"pages/{page_id}")
    
    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a POST request to the specified Notion API endpoint.

        Args:
            endpoint: The relative API path.
            data: Optional dictionary payload to send with the request.

        Returns:
            A dictionary with the response data, or None if the request failed.
        """
        return await self._make_request(HttpMethod.POST, endpoint, data)

    async def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a PATCH request to the specified Notion API endpoint.

        Args:
            endpoint: The relative API path.
            data: Optional dictionary payload to send with the request.

        Returns:
            A dictionary with the response data, or None if the request failed.
        """
        return await self._make_request(HttpMethod.PATCH, endpoint, data)

    async def delete(self, endpoint: str) -> bool:
        """
        Sends a DELETE request to the specified Notion API endpoint.

        Args:
            endpoint: The relative API path.

        Returns:
            True if the request was successful, False otherwise.
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
        Führt eine HTTP-Anfrage aus und gibt direkt die Daten zurück oder None bei Fehler.
        """
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
                response = await getattr(self.client, method_str)(url, json=data)
            else:
                response = await getattr(self.client, method_str)(url)

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

    def __del__(self):
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
