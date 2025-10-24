from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Self

from notionary.user.service import UserService
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder
from notionary.workspace.query.models import WorkspaceQueryConfig, WorkspaceQueryObjectType
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary import NotionDataSource, NotionPage
    from notionary.user import BotUser, PersonUser


class NotionWorkspace:
    def __init__(
        self,
        name: str | None = None,
        query_service: WorkspaceQueryService | None = None,
        user_service: UserService | None = None,
    ) -> None:
        self._name = name
        self._query_service = query_service or WorkspaceQueryService()
        self._user_service = user_service or UserService()

    @classmethod
    async def from_current_integration(cls) -> Self:
        from notionary.user import BotUser

        bot_user = await BotUser.from_current_integration()

        return cls(name=bot_user.workspace_name)

    @property
    def name(self) -> str:
        return self._name

    async def get_pages(
        self,
        *,
        filter_fn: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder] | None = None,
        query_config: WorkspaceQueryConfig | None = None,
    ) -> list[NotionPage]:
        if filter_fn is not None and query_config is not None:
            raise ValueError("Use either filter_fn OR query_config, not both")

        resolved_config = self._resolve_query_config(filter_fn, query_config, WorkspaceQueryObjectType.PAGE)
        return await self._query_service.get_pages(resolved_config)

    async def get_pages_stream(
        self,
        *,
        filter_fn: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder] | None = None,
        query_config: WorkspaceQueryConfig | None = None,
    ) -> AsyncIterator[NotionPage]:
        if filter_fn is not None and query_config is not None:
            raise ValueError("Use either filter_fn OR query_config, not both")

        resolved_config = self._resolve_query_config(filter_fn, query_config, WorkspaceQueryObjectType.PAGE)
        async for page in self._query_service.get_pages_stream(resolved_config):
            yield page

    async def get_data_sources(
        self,
        *,
        filter_fn: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder] | None = None,
        query_config: WorkspaceQueryConfig | None = None,
    ) -> list[NotionDataSource]:
        if filter_fn is not None and query_config is not None:
            raise ValueError("Use either filter_fn OR query_config, not both")

        resolved_config = self._resolve_query_config(filter_fn, query_config, WorkspaceQueryObjectType.DATA_SOURCE)
        return await self._query_service.get_data_sources(resolved_config)

    async def get_data_sources_stream(
        self,
        *,
        filter_fn: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder] | None = None,
        query_config: WorkspaceQueryConfig | None = None,
    ) -> AsyncIterator[NotionDataSource]:
        if filter_fn is not None and query_config is not None:
            raise ValueError("Use either filter_fn OR query_config, not both")

        resolved_config = self._resolve_query_config(filter_fn, query_config, WorkspaceQueryObjectType.DATA_SOURCE)
        async for data_source in self._query_service.get_data_sources_stream(resolved_config):
            yield data_source

    def _resolve_query_config(
        self,
        filter_fn: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder] | None,
        query_config: WorkspaceQueryConfig | None,
        expected_object_type: WorkspaceQueryObjectType,
    ) -> WorkspaceQueryConfig:
        if filter_fn is not None:
            builder = NotionWorkspaceQueryConfigBuilder()
            configured_builder = filter_fn(builder)
            query_config = configured_builder.build()

        if query_config is None:
            query_config = WorkspaceQueryConfig(object_type=expected_object_type)
        else:
            query_config.object_type = expected_object_type

        return query_config

    async def get_users(self) -> list[PersonUser]:
        return [user async for user in self._user_service.list_users_stream()]

    async def get_users_stream(self) -> AsyncIterator[PersonUser]:
        async for user in self._user_service.list_users_stream():
            yield user

    async def get_bot_users(self) -> list[BotUser]:
        return [user async for user in self._user_service.list_bot_users_stream()]

    async def get_bot_users_stream(self) -> AsyncIterator[BotUser]:
        async for user in self._user_service.list_bot_users_stream():
            yield user

    async def search_users(self, query: str) -> list[PersonUser]:
        return [user async for user in self._user_service.search_users_stream(query)]

    async def search_users_stream(self, query: str) -> AsyncIterator[PersonUser]:
        async for user in self._user_service.search_users_stream(query):
            yield user
