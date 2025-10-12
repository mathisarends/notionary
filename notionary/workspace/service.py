from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Self

from notionary.user.service import UserService
from notionary.workspace.query.builder import WorkspaceQueryConfigBuilder
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource
    from notionary.page.service import NotionPage
    from notionary.user import BotUser, PersonUser


# TODO: Make this here less redundant and allow for querying options (the query builder should not be used in client at all but rather its result)
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

    def filter(self) -> WorkspaceQueryConfigBuilder:
        return WorkspaceQueryConfigBuilder()

    async def query_pages(
        self, filter_fn: Callable[[WorkspaceQueryConfigBuilder], WorkspaceQueryConfigBuilder]
    ) -> list[NotionPage]:
        builder = WorkspaceQueryConfigBuilder()
        filter_fn(builder)
        search_config = builder.config

        return [page async for page in self._query_service.query_pages_stream(search_config)]

    async def query_pages_stream(
        self, filter_fn: Callable[[WorkspaceQueryConfigBuilder], WorkspaceQueryConfigBuilder]
    ) -> AsyncIterator[NotionPage]:
        builder = WorkspaceQueryConfigBuilder()
        filter_fn(builder)
        search_config = builder.config

        async for page in self._query_service.query_pages_stream(search_config):
            yield page

    async def query_data_sources(
        self, filter_fn: Callable[[WorkspaceQueryConfigBuilder], WorkspaceQueryConfigBuilder]
    ) -> list[NotionDataSource]:
        builder = WorkspaceQueryConfigBuilder()
        filter_fn(builder)
        search_config = builder.config

        return [data_source async for data_source in self._query_service.query_data_sources_stream(search_config)]

    async def query_data_sources_stream(
        self, filter_fn: Callable[[WorkspaceQueryConfigBuilder], WorkspaceQueryConfigBuilder]
    ) -> AsyncIterator[NotionDataSource]:
        builder = WorkspaceQueryConfigBuilder()
        filter_fn(builder)
        search_config = builder.config

        async for data_source in self._query_service.query_data_sources_stream(search_config):
            yield data_source

    async def get_data_sources(self, page_size: int | None = None) -> list[NotionDataSource]:
        return [data_source async for data_source in self._query_service.get_data_sources_stream(page_size=page_size)]

    async def get_data_sources_stream(self, page_size: int | None = None) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.get_data_sources_stream(page_size=page_size):
            yield data_source

    async def search_data_sources(self, query: str, page_size: int | None = None) -> list[NotionDataSource]:
        return [ds async for ds in self._query_service.search_data_sources_stream(query, page_size=page_size)]

    async def search_data_sources_stream(
        self, query: str, page_size: int | None = None
    ) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.search_data_sources_stream(query, page_size=page_size):
            yield data_source

    async def get_pages(self, page_size: int | None = None) -> list[NotionPage]:
        return [page async for page in self._query_service.get_pages_stream(page_size=page_size)]

    async def get_pages_stream(self, page_size: int | None = None) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.get_pages_stream(page_size=page_size):
            yield page

    async def search_pages(self, query: str, page_size: int | None = None) -> list[NotionPage]:
        return [page async for page in self._query_service.search_pages_stream(query, page_size=page_size)]

    async def search_pages_stream(self, query: str, page_size: int | None = None) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.search_pages_stream(query, page_size=page_size):
            yield page

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
