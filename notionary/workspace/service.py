from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Self

from notionary.user.service import UserService
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder
from notionary.workspace.query.models import WorkspaceQueryConfig, WorkspaceQueryObjectType
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource
    from notionary.page.service import NotionPage
    from notionary.user import BotUser, PersonUser

type _QueryConfigInput = (
    WorkspaceQueryConfig | Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder]
)


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
        config: _QueryConfigInput | None = None,
    ) -> list[NotionPage]:
        query_config = self._resolve_config(config, WorkspaceQueryObjectType.PAGE)
        return await self._query_service.get_pages(query_config)

    async def get_pages_stream(
        self,
        config: _QueryConfigInput | None = None,
    ) -> AsyncIterator[NotionPage]:
        query_config = self._resolve_config(config, WorkspaceQueryObjectType.PAGE)
        async for page in self._query_service.get_pages_stream(query_config):
            yield page

    async def get_data_sources(
        self,
        config: _QueryConfigInput | None = None,
    ) -> list[NotionDataSource]:
        query_config = self._resolve_config(config, WorkspaceQueryObjectType.DATA_SOURCE)
        return await self._query_service.get_data_sources(query_config)

    async def get_data_sources_stream(
        self,
        config: _QueryConfigInput | None = None,
    ) -> AsyncIterator[NotionDataSource]:
        query_config = self._resolve_config(config, WorkspaceQueryObjectType.DATA_SOURCE)
        async for data_source in self._query_service.get_data_sources_stream(query_config):
            yield data_source

    def _resolve_config(
        self,
        config: _QueryConfigInput | None,
        expected_object_type: WorkspaceQueryObjectType,
    ) -> WorkspaceQueryConfig:
        if config is None:
            return self._create_default_config(expected_object_type)

        if isinstance(config, WorkspaceQueryConfig):
            return self._ensure_correct_object_type(config, expected_object_type)

        return self._build_config_from_callable(config, expected_object_type)

    def _create_default_config(self, object_type: WorkspaceQueryObjectType) -> WorkspaceQueryConfig:
        return WorkspaceQueryConfig(object_type=object_type)

    def _build_config_from_callable(
        self,
        config_callable: Callable[[NotionWorkspaceQueryConfigBuilder], NotionWorkspaceQueryConfigBuilder],
        expected_object_type: WorkspaceQueryObjectType,
    ) -> WorkspaceQueryConfig:
        builder = NotionWorkspaceQueryConfigBuilder()
        config_callable(builder)
        return self._ensure_correct_object_type(builder.build(), expected_object_type)

    def _ensure_correct_object_type(
        self,
        config: WorkspaceQueryConfig,
        expected_object_type: WorkspaceQueryObjectType,
    ) -> WorkspaceQueryConfig:
        config.object_type = expected_object_type
        return config

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
