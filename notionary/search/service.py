from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.search.client import SearchClient
from notionary.search.exceptions import DatabaseNotFound, DataSourceNotFound, PageNotFound
from notionary.utils.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage


class SearchableEntity(asyncio.Protocol):
    title: str


class SearchService:
    def __init__(self, client: SearchClient | None = None) -> None:
        self._client = client or SearchClient()

    async def find_data_source(self, query: str = "", min_similarity: float = 0.6) -> NotionDataSource:
        data_sources = await self._search_data_sources(query)
        return self._get_best_match(
            data_sources, query, exception_class=DataSourceNotFound, min_similarity=min_similarity
        )

    async def find_page(self, query: str = "", min_similarity: float = 0.6) -> NotionPage:
        pages = await self._search_pages(query)
        return self._get_best_match(pages, query, exception_class=PageNotFound, min_similarity=min_similarity)

    async def find_database(self, query: str = "") -> NotionDatabase:
        data_sources = await self._search_data_sources(query)

        parent_databases = await asyncio.gather(*(data_source.get_parent_database() for data_source in data_sources))
        potential_databases = [db for db in parent_databases if db is not None]

        return self._get_best_match(potential_databases, query, exception_class=DatabaseNotFound)

    async def _search_pages(self, query: str) -> list[NotionPage]:
        from notionary import NotionPage

        page_search_response = await self._client.fetch_pages(query)
        return await asyncio.gather(*(NotionPage.from_id(page.id) for page in page_search_response.results))

    async def _search_data_sources(self, query: str = "") -> list[NotionDataSource]:
        from notionary import NotionDataSource

        data_source_search_response = await self._client.fetch_data_sources(query)
        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source.id) for data_source in data_source_search_response.results)
        )

    def _get_best_match(
        self,
        search_results: list[SearchableEntity],
        query: str,
        exception_class: type[Exception],
        min_similarity: float | None = None,
    ) -> SearchableEntity:
        best_match = find_best_match(
            query=query,
            items=search_results,
            text_extractor=lambda searchable_entity: searchable_entity.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in search_results[:5]]
            raise exception_class(query, available_titles)

        return best_match
