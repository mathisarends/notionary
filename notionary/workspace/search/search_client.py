from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.http.http_client import NotionHttpClient
from notionary.utils.fuzzy import find_best_match
from notionary.workspace.search.search_filter_builder import SearchFilterBuilder, SortDirection
from notionary.workspace.search.search_models import DataSourceSearchResponse, PageSearchResponse

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage


class SearchableEntity(asyncio.Protocol):
    title: str


class SearchClient(NotionHttpClient):
    def __init__(self, timeout: int = 30) -> None:
        super().__init__(timeout)

    async def find_data_source(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100, min_similarity: float = 0.6
    ) -> NotionDataSource | None:
        data_sources = await self.search_data_sources(query, sort_ascending, limit)
        return self._get_best_match(data_sources, query, min_similarity=min_similarity)

    async def find_page(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100, min_similarity: float = 0.6
    ) -> NotionPage | None:
        pages = await self.search_pages(query, sort_ascending, limit)
        return self._get_best_match(pages, query, min_similarity=min_similarity)

    async def find_database(self, query: str = "", sort_ascending: bool = True, limit: int = 100) -> NotionDatabase:
        data_sources = await self.search_data_sources(query, sort_ascending, limit)

        parent_databases = await asyncio.gather(*(data_source.get_parent_database() for data_source in data_sources))
        potential_databases = [db for db in parent_databases if db is not None]

        return self._get_best_match(potential_databases, query)

    async def search_pages(self, query: str, sort_ascending: bool = True, limit=100) -> None:
        from notionary import NotionPage

        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_sort_direction(SortDirection.ASCENDING if sort_ascending else SortDirection.DESCENDING)
            .with_pages_only()
            .with_page_size(100)
        )

        search_data = search_filter.build()
        response = await self.post("search", search_data)

        page_search_response = PageSearchResponse.model_validate(response)
        return await asyncio.gather(*(NotionPage.from_id(page.id) for page in page_search_response.results))

    async def search_data_sources(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> list[NotionDataSource]:
        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_data_sources_only()
            .with_sort_direction(SortDirection.ASCENDING if sort_ascending else SortDirection.DESCENDING)
            .with_page_size(limit)
        )

        search_data = search_filter.build()
        response = await self.post("search", search_data)
        data_source_search_response = DataSourceSearchResponse.model_validate(response)

        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source.id) for data_source in data_source_search_response.results)
        )

    def _get_best_match(
        self, search_results: list[SearchableEntity], query: str, min_similarity: float | None = None
    ) -> NotionDataSource | None:
        best_match = find_best_match(
            query=query,
            items=search_results,
            text_extractor=lambda searchable_entity: searchable_entity.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in search_results[:5]]
            raise ValueError(f"No sufficiently similar entity found for '{query}'. Available: {available_titles}")

        return best_match
