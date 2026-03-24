from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from notionary.http.client import HttpClient
from notionary.user.client import UserHttpClient
from notionary.user.namespace import UserService
from notionary.workspace.client import WorkspaceClient
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder
from notionary.workspace.query.models import (
    WorkspaceQueryConfig,
    WorkspaceQueryObjectType,
)
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary import NotionDataSource, NotionPage


class WorkspaceNamespace:
    def __init__(self, http: HttpClient) -> None:
        workspace_client = WorkspaceClient(http)
        self._query_service = WorkspaceQueryService(workspace_client)
        self._user_service = UserService(UserHttpClient(http))

    def get_query_builder(self) -> NotionWorkspaceQueryConfigBuilder:
        return NotionWorkspaceQueryConfigBuilder()

    async def list_pages(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> list[NotionPage]:
        config = self._pages_config(query_config)
        return await self._query_service.get_pages(config)

    async def get_pages(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> list[NotionPage]:
        return await self.list_pages(query_config)

    async def iter_pages(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> AsyncIterator[NotionPage]:
        config = self._pages_config(query_config)
        async for page in self._query_service.get_pages_stream(config):
            yield page

    async def list_pages_stream(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> AsyncIterator[NotionPage]:
        async for page in self.iter_pages(query_config):
            yield page

    async def get_data_sources(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> list[NotionDataSource]:
        config = self._data_sources_config(query_config)
        return await self._query_service.get_data_sources(config)

    async def iter_data_sources(
        self, query_config: WorkspaceQueryConfig | None = None
    ) -> AsyncIterator[NotionDataSource]:
        config = self._data_sources_config(query_config)
        async for ds in self._query_service.get_data_sources_stream(config):
            yield ds

    @staticmethod
    def _pages_config(
        query_config: WorkspaceQueryConfig | None,
    ) -> WorkspaceQueryConfig:
        if query_config is None:
            return WorkspaceQueryConfig(object_type=WorkspaceQueryObjectType.PAGE)
        query_config.object_type = WorkspaceQueryObjectType.PAGE
        return query_config

    @staticmethod
    def _data_sources_config(
        query_config: WorkspaceQueryConfig | None,
    ) -> WorkspaceQueryConfig:
        if query_config is None:
            return WorkspaceQueryConfig(
                object_type=WorkspaceQueryObjectType.DATA_SOURCE
            )
        query_config.object_type = WorkspaceQueryObjectType.DATA_SOURCE
        return query_config
