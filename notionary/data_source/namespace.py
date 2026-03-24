import difflib
from collections.abc import AsyncIterator

from notionary.data_source.data_source import DataSource
from notionary.data_source.search import (
    DataSourceSearchClient,
    SortDirection,
    SortTimestamp,
)
from notionary.exceptions.search import DataSourceNotFound
from notionary.http.client import HttpClient


def _fuzzy_suggestions(
    query: str, items: list[DataSource], top_n: int = 5
) -> list[str]:
    scored = [
        (item, difflib.SequenceMatcher(None, query.lower(), item.title.lower()).ratio())
        for item in items
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [item.title for item, score in scored[:top_n] if score >= 0.6]


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
        candidates = await self.list(query=title, page_size=100)

        exact = next(
            (ds for ds in candidates if ds.title.lower() == title.lower()), None
        )
        if exact:
            return exact

        suggestions = _fuzzy_suggestions(title, candidates)
        raise DataSourceNotFound(title, suggestions)

    async def from_id(self, data_source_id: str) -> DataSource:
        return await DataSource.from_id(data_source_id)
