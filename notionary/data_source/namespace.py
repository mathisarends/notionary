from collections.abc import AsyncIterator

from notionary.data_source.data_source import DataSource
from notionary.data_source.search import (
    DataSourceSearchClient,
    SortDirection,
    SortTimestamp,
)
from notionary.http.client import HttpClient


class DataSourceNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._search_client = DataSourceSearchClient(http)

    async def list(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[DataSource]:
        return [
            ds
            async for ds in self.iter(
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
    ) -> AsyncIterator[DataSource]:
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield await DataSource.from_id(dto.id)

    async def search(self, query: str) -> list[DataSource]:
        return await self.list(query=query)

    async def from_title(self, title: str) -> DataSource:
        return await DataSource.from_title(title)

    async def from_id(self, data_source_id: str) -> DataSource:
        return await DataSource.from_id(data_source_id)
