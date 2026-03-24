import logging
from typing import Any

import httpx

from notionary.http.exceptions import (
    NotionAuthenticationError,
    NotionError,
    NotionNotFoundError,
    NotionPermissionError,
    NotionRateLimitError,
    NotionServerError,
    NotionValidationError,
)

logger = logging.getLogger(__name__)


class HttpClient:
    _BASE_URL = "https://api.notion.com/v1"
    _NOTION_VERSION = "2025-09-03"

    def __init__(self, token: str, timeout: int = 30) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": self._NOTION_VERSION,
            },
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("POST", endpoint, json=data)

    async def patch(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self._request("PATCH", endpoint, json=data)

    async def delete(self, endpoint: str) -> dict[str, Any]:
        return await self._request("DELETE", endpoint)

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        url = f"{self._BASE_URL}/{endpoint.lstrip('/')}"
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        logger.debug("%s %s", method, url)
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise self._map_error(e) from e

    @staticmethod
    def _map_error(e: httpx.HTTPStatusError) -> NotionError:
        match e.response.status_code:
            case 400:
                return NotionValidationError(e.response.text)
            case 401:
                return NotionAuthenticationError(e.response.text)
            case 403:
                return NotionPermissionError(e.response.text)
            case 404:
                return NotionNotFoundError(e.response.text)
            case 429:
                return NotionRateLimitError(e.response.text)
            case c if 500 <= c < 600:
                return NotionServerError(e.response.text)
            case _:
                return NotionError(e.response.text)
