from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Protocol

from notionary.exceptions.search import DatabaseNotFound, DataSourceNotFound, PageNotFound
from notionary.utils.fuzzy import find_best_match
from notionary.workspace.client import WorkspaceClient
from notionary.workspace.query.builder import WorkspaceQueryConfigBuilder
from notionary.workspace.query.models import WorkspaceQueryConfig

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage


class SearchableEntity(Protocol):
    title: str


class WorkspaceQueryService:
    def __init__(self, client: WorkspaceClient | None = None) -> None:
        self._client = client or WorkspaceClient()

    async def get_pages_stream(self, search_config: WorkspaceQueryConfig) -> AsyncIterator[NotionPage]:
        from notionary import NotionPage

        async for page_dto in self._client.query_pages_stream(search_config):
            yield await NotionPage.from_id(page_dto.id)

    async def get_pages(self, search_config: WorkspaceQueryConfig) -> list[NotionPage]:
        from notionary import NotionPage

        page_dtos = [dto async for dto in self._client.query_pages_stream(search_config)]
        page_tasks = [NotionPage.from_id(dto.id) for dto in page_dtos]
        return await asyncio.gather(*page_tasks)

    async def get_data_sources_stream(self, search_config: WorkspaceQueryConfig) -> AsyncIterator[NotionDataSource]:
        from notionary import NotionDataSource

        async for data_source_dto in self._client.query_data_sources_stream(search_config):
            yield await NotionDataSource.from_id(data_source_dto.id)

    async def get_data_sources(self, search_config: WorkspaceQueryConfig) -> list[NotionDataSource]:
        from notionary import NotionDataSource

        data_source_dtos = [dto async for dto in self._client.query_data_sources_stream(search_config)]
        data_source_tasks = [NotionDataSource.from_id(dto.id) for dto in data_source_dtos]
        return await asyncio.gather(*data_source_tasks)

    async def find_data_source(self, query: str, min_similarity: float = 0.6) -> NotionDataSource:
        config = WorkspaceQueryConfigBuilder().with_query(query).with_data_sources_only().with_page_size(5).build()
        data_sources = await self.get_data_sources(config)

        return self._get_best_match(
            data_sources, query, exception_class=DataSourceNotFound, min_similarity=min_similarity
        )

    async def find_page(self, query: str, min_similarity: float = 0.6) -> NotionPage:
        config = WorkspaceQueryConfigBuilder().with_query(query).with_pages_only().with_page_size(5).build()
        pages = await self.get_pages(config)

        return self._get_best_match(pages, query, exception_class=PageNotFound, min_similarity=min_similarity)

    async def find_database(self, query: str = "") -> NotionDatabase:
        config = WorkspaceQueryConfigBuilder().with_query(query).with_data_sources_only().with_page_size(100).build()
        data_sources = await self.get_data_sources(config)

        parent_database_tasks = [data_source.get_parent_database() for data_source in data_sources]
        parent_databases = await asyncio.gather(*parent_database_tasks)
        potential_databases = [database for database in parent_databases if database is not None]

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
