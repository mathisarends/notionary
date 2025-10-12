from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Protocol

from notionary.exceptions.search import DatabaseNotFound, DataSourceNotFound, PageNotFound
from notionary.utils.fuzzy import find_best_match
from notionary.workspace.client import WorkspaceClient

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage
    from notionary.workspace.query.models import WorkspaceQueryConfig


class SearchableEntity(Protocol):
    title: str


class WorkspaceQueryService:
    def __init__(self, client: WorkspaceClient | None = None) -> None:
        self._client = client or WorkspaceClient()

    async def get_pages_stream(self, page_size: int | None = None) -> AsyncIterator[NotionPage]:
        from notionary import NotionPage

        async for page_dto in self._client.get_pages_stream(page_size=page_size):
            yield await NotionPage.from_id(page_dto.id)

    async def search_pages_stream(self, query: str, page_size: int | None = None) -> AsyncIterator[NotionPage]:
        from notionary import NotionPage

        async for page_dto in self._client.search_pages_stream(query, page_size=page_size):
            yield await NotionPage.from_id(page_dto.id)

    async def query_pages_stream(self, search_config: WorkspaceQueryConfig) -> AsyncIterator[NotionPage]:
        from notionary import NotionPage

        async for page_dto in self._client.query_stream(search_config):
            yield await NotionPage.from_id(page_dto.id)

    async def get_data_sources_stream(self, page_size: int | None = None) -> AsyncIterator[NotionDataSource]:
        from notionary import NotionDataSource

        async for data_source_dto in self._client.get_data_sources_stream(page_size=page_size):
            yield await NotionDataSource.from_id(data_source_dto.id)

    async def search_data_sources_stream(
        self, query: str, page_size: int | None = None
    ) -> AsyncIterator[NotionDataSource]:
        from notionary import NotionDataSource

        async for data_source_dto in self._client.search_data_sources_stream(query, page_size=page_size):
            yield await NotionDataSource.from_id(data_source_dto.id)

    async def query_data_sources_stream(self, search_config: WorkspaceQueryConfig) -> AsyncIterator[NotionDataSource]:
        from notionary import NotionDataSource

        async for data_source_dto in self._client.query_stream(search_config):
            yield await NotionDataSource.from_id(data_source_dto.id)

    async def find_data_source(self, query: str, min_similarity: float = 0.6) -> NotionDataSource:
        data_sources = [ds async for ds in self.search_data_sources_stream(query)]
        return self._get_best_match(
            data_sources, query, exception_class=DataSourceNotFound, min_similarity=min_similarity
        )

    async def find_page(self, query: str, min_similarity: float = 0.6) -> NotionPage:
        pages = [page async for page in self.search_pages_stream(query)]
        return self._get_best_match(pages, query, exception_class=PageNotFound, min_similarity=min_similarity)

    async def find_database(self, query: str = "") -> NotionDatabase:
        data_sources = [ds async for ds in self.search_data_sources_stream(query)]

        parent_databases = await asyncio.gather(*(data_source.get_parent_database() for data_source in data_sources))
        potential_databases = [db for db in parent_databases if db is not None]

        return self._get_best_match(potential_databases, query, exception_class=DatabaseNotFound)

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
