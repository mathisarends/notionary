import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx
from pydantic import BaseModel

from notionary.http.schemas import PaginatedResponse

logger = logging.getLogger(__name__)


class HttpClient:
    _BASE_URL = "https://api.notion.com/v1"
    _NOTION_VERSION = "2026-03-11"

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
        self,
        endpoint: str,
        data: BaseModel | dict[str, Any] | None = None,
        *,
        exclude_unset: bool = False,
    ) -> dict[str, Any]:
        return await self._request(
            "POST", endpoint, json=self._serialize(data, exclude_unset)
        )

    async def post_multipart(
        self, endpoint: str, files: dict[str, Any], data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self._BASE_URL}/{endpoint.lstrip('/')}"
        logger.debug("POST multipart %s", url)
        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()

    async def patch(
        self,
        endpoint: str,
        data: BaseModel | dict[str, Any] | None = None,
        *,
        exclude_unset: bool = False,
    ) -> dict[str, Any]:
        return await self._request(
            "PATCH", endpoint, json=self._serialize(data, exclude_unset)
        )

    async def delete(self, endpoint: str) -> dict[str, Any]:
        return await self._request("DELETE", endpoint)

    @staticmethod
    def _serialize(
        data: BaseModel | dict[str, Any] | None, exclude_unset: bool
    ) -> dict[str, Any] | None:
        if data is None:
            return None
        if isinstance(data, BaseModel):
            return data.model_dump(
                exclude_none=True, exclude_unset=exclude_unset, mode="json"
            )
        return data

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        url = f"{self._BASE_URL}/{endpoint.lstrip('/')}"
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        logger.debug("%s %s", method, url)
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def paginate(
        self,
        endpoint: str,
        total_results_limit: int | None = None,
        **kwargs,
    ) -> list[Any]:
        results: list[Any] = []
        async for page in self._fetch_pages(endpoint, total_results_limit, **kwargs):
            results.extend(page.results)
        return results

    async def paginate_stream(
        self,
        endpoint: str,
        total_results_limit: int | None = None,
        **kwargs,
    ) -> AsyncGenerator[Any]:
        async for page in self._fetch_pages(endpoint, total_results_limit, **kwargs):
            for item in page.results:
                yield item

    async def _fetch_pages(
        self,
        endpoint: str,
        total_results_limit: int | None = None,
        method: str = "POST",
        **kwargs,
    ) -> AsyncGenerator[PaginatedResponse]:
        next_cursor: str | None = None
        has_more = True
        total_fetched = 0
        api_page_size: int = kwargs.get("page_size", 100)

        while has_more and self._below_limit(total_results_limit, total_fetched):
            params = {**kwargs}
            if next_cursor:
                params["start_cursor"] = next_cursor

            if method.upper() == "GET":
                raw = await self.get(endpoint, params=params)
            else:
                raw = await self.post(endpoint, data=params)
            response = PaginatedResponse.model_validate(raw)

            results = self._slice_to_limit(
                response.results, total_results_limit, total_fetched
            )
            total_fetched += len(results)

            yield self._build_page_response(response, results, api_page_size)

            if not self._below_limit(total_results_limit, total_fetched):
                break

            has_more = response.has_more
            next_cursor = response.next_cursor

    @staticmethod
    def _below_limit(limit: int | None, fetched: int) -> bool:
        return limit is None or fetched < limit

    @staticmethod
    def _slice_to_limit(
        results: list[Any], limit: int | None, fetched: int
    ) -> list[Any]:
        if limit is None:
            return results
        return results[: limit - fetched]

    @staticmethod
    def _build_page_response(
        original: PaginatedResponse,
        results: list[Any],
        api_page_size: int,
    ) -> PaginatedResponse:
        client_truncated = len(results) < len(original.results)
        full_page = len(original.results) == api_page_size
        has_more = original.has_more and not client_truncated and full_page

        return PaginatedResponse(
            results=results,
            has_more=has_more,
            next_cursor=original.next_cursor if has_more else None,
        )
