import asyncio
import os
from enum import Enum
from typing import Dict, Any, Optional, Union
import httpx
from dotenv import load_dotenv
from notionary.models.notion_database_response import (
    NotionDatabaseResponse,
    NotionDatabaseSearchResponse,
    NotionQueryDatabaseResponse,
)
from notionary.models.notion_page_response import NotionPageResponse
from notionary.util import LoggingMixin, singleton

load_dotenv()


class HttpMethod(Enum):
    """
    Enumeration of supported HTTP methods for API requests.

    Attributes:
        GET:    HTTP GET method, used for retrieving data.
        POST:   HTTP POST method, used for creating resources or sending data.
        PATCH:  HTTP PATCH method, used for partial updates of resources.
        DELETE: HTTP DELETE method, used for deleting resources.
    """

    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


@singleton
class NotionClient(LoggingMixin):
    """Verbesserter Notion-Client mit automatischer Ressourcenverwaltung."""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        self.token = token or self.find_token()
        if not self.token:
            raise ValueError("Notion API token is required")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

        self.client = httpx.AsyncClient(headers=self.headers, timeout=timeout)

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

    async def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Sends a GET request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.GET, endpoint)

    async def get_database(self, database_id: str) -> NotionDatabaseResponse:
        """
        Gets metadata for a Notion database by its ID.
        """
        response = await self.get(f"databases/{database_id}")
        return NotionDatabaseResponse.model_validate(response)

    async def create_page(
        self, parent_database_id: Optional[str]
    ) -> NotionPageResponse:
        response = await self.post(
            "pages", {"parent": {"database_id": parent_database_id}, "properties": {}}
        )

        return NotionPageResponse.model_validate(response)

    async def query_database(
        self, database_id, query_data: Dict[str, Any]
    ) -> NotionQueryDatabaseResponse:
        """
        Queries a Notion database with the provided filter and sorts.
        """
        result = await self.post(f"databases/{database_id}/query", data=query_data)
        print(f"Querying database {database_id} with data: {query_data}")
        print("Query result:", result)
        return NotionQueryDatabaseResponse.model_validate(result)

    async def query_database_by_title(
        self, database_id: str, page_title: str
    ) -> NotionQueryDatabaseResponse:
        """
        Queries a Notion database by title and returns the database response.
        """
        query_data = {
            "filter": {"property": "title", "title": {"contains": page_title}}
        }

        result = await self.query_database(
            database_id=database_id, query_data=query_data
        )
        return NotionQueryDatabaseResponse.model_validate(result)

    async def search_pages(
        self, query: str, sort_ascending=True, limit=100
    ) -> NotionQueryDatabaseResponse:
        """
        Searches for pages in Notion using the search endpoint.
        """
        sort_order = "ascending" if sort_ascending else "descending"

        search_payload = {
            "query": query,
            "filter": {"property": "object", "value": "page"},
            "sort": {"direction": sort_order, "timestamp": "last_edited_time"},
            "page_size": min(limit, 100),
        }

        result = await self.post("search", search_payload)
        return NotionQueryDatabaseResponse.model_validate(result)

    async def search_databases(
        self, query: str, sort_ascending: bool = True, limit: int = 100
    ) -> NotionDatabaseSearchResponse:
        """
        Searches for databases in Notion using the search endpoint.
        """
        sort_order = "ascending" if sort_ascending else "descending"
        search_payload = {
            "query": query,
            "filter": {"property": "object", "value": "database"},
            "sort": {"direction": sort_order, "timestamp": "last_edited_time"},
            "page_size": min(limit, 100),
        }
        result = await self.post("search", search_payload)
        return NotionDatabaseSearchResponse.model_validate(result)

    async def get_page(self, page_id: str) -> NotionPageResponse:
        """
        Gets metadata for a Notion page by its ID.
        """
        return NotionPageResponse.model_validate(await self.get(f"pages/{page_id}"))

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a POST request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.POST, endpoint, data)

    async def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends a PATCH request to the specified Notion API endpoint.
        """
        return await self._make_request(HttpMethod.PATCH, endpoint, data)

    async def patch_page(
        self, page_id: str, data: Optional[Dict[str, Any]] = None
    ) -> NotionPageResponse:
        """
        Sends a PATCH request to update a Notion page.
        """
        return NotionPageResponse.model_validate(
            await self.patch(f"pages/{page_id}", data=data)
        )

    async def delete(self, endpoint: str) -> bool:
        """
        Sends a DELETE request to the specified Notion API endpoint.
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

    async def close(self):
        """
        Closes the HTTP client for this instance and releases resources.
        """
        if not hasattr(self, "client") or not self.client:
            return

        await self.client.aclose()
        self.client = None

    def find_token(self) -> Optional[str]:
        """
        Finds the Notion API token from environment variables or raises an error if not found.
        """
        for var in ("NOTION_SECRET", "NOTION_API_KEY", "NOTION_TOKEN"):
            token = os.getenv(var)
            if token:
                return token
        return None
