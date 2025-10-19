from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from notionary.exceptions.search import DatabaseNotFound, DataSourceNotFound, PageNotFound
from notionary.utils.fuzzy import find_all_matches
from notionary.workspace.client import WorkspaceClient
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder
from notionary.workspace.query.models import SearchableEntity, WorkspaceQueryConfig

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage


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

    async def find_data_source(self, query: str) -> NotionDataSource:
        config = (
            NotionWorkspaceQueryConfigBuilder().with_query(query).with_data_sources_only().with_page_size(100).build()
        )
        data_sources = await self.get_data_sources(config)
        return self._find_exact_match(data_sources, query, DataSourceNotFound)

    async def find_page(self, query: str) -> NotionPage:
        config = NotionWorkspaceQueryConfigBuilder().with_query(query).with_pages_only().with_page_size(100).build()
        pages = await self.get_pages(config)
        return self._find_exact_match(pages, query, PageNotFound)

    async def find_database(self, query: str) -> NotionDatabase:
        config = (
            NotionWorkspaceQueryConfigBuilder().with_query(query).with_data_sources_only().with_page_size(100).build()
        )
        data_sources = await self.get_data_sources(config)

        parent_database_ids = [data_sources.get_parent_database_id_if_present() for data_sources in data_sources]
        # filter none values which should not happen but for safety
        parent_database_ids = [id for id in parent_database_ids if id is not None]

        parent_database_tasks = [NotionDatabase.from_id(db_id) for db_id in parent_database_ids]
        parent_databases = await asyncio.gather(*parent_database_tasks)
        potential_databases = [database for database in parent_databases if database is not None]

        return self._find_exact_match(potential_databases, query, DatabaseNotFound)

    def _find_exact_match(
        self,
        search_results: list[SearchableEntity],
        query: str,
        exception_class: type[Exception],
    ) -> SearchableEntity:
        if not search_results:
            raise exception_class(query, [])

        query_lower = query.lower()
        exact_matches = [result for result in search_results if result.title.lower() == query_lower]

        if exact_matches:
            return exact_matches[0]

        suggestions = self._get_fuzzy_suggestions(search_results, query)
        raise exception_class(query, suggestions)

    def _get_fuzzy_suggestions(self, search_results: list[SearchableEntity], query: str) -> list[str]:
        sorted_by_similarity = find_all_matches(
            query=query,
            items=search_results,
            text_extractor=lambda entity: entity.title,
            min_similarity=0.6,
        )

        if sorted_by_similarity:
            return [result.title for result in sorted_by_similarity[:5]]

        return [result.title for result in search_results[:5]]
