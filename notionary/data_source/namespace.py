from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

from notionary.data_source.data_source import DataSource
from notionary.data_source.exceptions import DataSourceNotFound
from notionary.data_source.mapper import to_data_source
from notionary.data_source.schemas import DataSourceDto
from notionary.data_source.search import (
    DataSourceSearchClient,
    SortDirection,
    SortTimestamp,
)
from notionary.http import HttpClient
from notionary.shared.search import fuzzy_suggestions


class DataSourceNamespace:
    """Scoped access to Notion data sources.

    Provides listing, searching, and retrieval of
    :class:`~notionary.data_source.data_source.DataSource` objects.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._search_client = DataSourceSearchClient(http)

    async def list(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[DataSource]:
        """Return data sources as a list, optionally filtered by a search query.

        Args:
            query: Optional text query to filter data sources by title.
            sort_direction: Sort order (ascending or descending).
            sort_timestamp: Sort by ``last_edited_time`` or ``created_time``.
            page_size: Number of results per API request.
            total_results_limit: Maximum total number of data sources to return.

        Returns:
            A list of matching :class:`~notionary.data_source.data_source.DataSource` objects.
        """
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
        """Yield data sources one by one without loading all results into memory.

        Accepts the same arguments as :meth:`list`.
        """
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield self._data_source_from_dto(dto)

    async def search(self, query: str) -> list[DataSource]:
        """Search data sources by title.

        Convenience alias for ``list(query=query)``.

        Args:
            query: Text query to match against data source titles.
        """
        return await self.list(query=query)

    async def find(self, title: str) -> DataSource:
        """Find a data source by its exact title (case-insensitive).

        Args:
            title: The data source title to search for.

        Returns:
            The matching :class:`~notionary.data_source.data_source.DataSource`.

        Raises:
            DataSourceNotFound: If no exact match is found. The exception
                includes fuzzy suggestions when available.
        """
        candidates = await self.list(query=title, page_size=10, total_results_limit=10)

        exact = next(
            (ds for ds in candidates if ds.title.lower() == title.lower()), None
        )
        if exact:
            return exact

        suggestions = fuzzy_suggestions(title, candidates)
        raise DataSourceNotFound(title, suggestions)

    async def from_id(self, data_source_id: UUID) -> DataSource:
        """Retrieve a data source by its UUID.

        Args:
            data_source_id: The Notion data source UUID.

        Returns:
            The :class:`~notionary.data_source.data_source.DataSource` for the given ID.
        """
        response = await self._http.get(f"databases/{data_source_id}")
        dto = DataSourceDto.model_validate(response)
        return self._data_source_from_dto(dto)

    def _data_source_from_dto(self, dto: DataSourceDto) -> DataSource:
        return to_data_source(dto, self._http)
