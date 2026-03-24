from collections.abc import AsyncIterator

from notionary.http.client import HttpClient
from notionary.page.search import PageSearchClient
from notionary.page.search.schemas import SortDirection, SortTimestamp
from notionary.page.service import NotionPage


class PageNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._search_client = PageSearchClient(http)

    async def list(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[NotionPage]:
        return [
            page
            async for page in self.iter(
                query=query,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                page_size=page_size,
                total_results_limit=total_results_limit,
            )
        ]

    async def iter(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> AsyncIterator[NotionPage]:
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield await NotionPage.from_id(dto.id)

    async def from_title(self, title: str) -> NotionPage:
        return await NotionPage.from_title(title)

    async def from_id(self, page_id: str) -> NotionPage:
        return await NotionPage.from_id(page_id)
