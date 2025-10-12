from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Self

from notionary.user.service import UserService
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource
    from notionary.page.service import NotionPage
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

    async def get_data_sources(self) -> list[NotionDataSource]:
        return [data_source async for data_source in self._query_service.get_data_sources_stream()]

    async def get_data_sources_stream(self) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.get_data_sources_stream():
            yield data_source

    async def search_data_sources(self, query: str) -> list[NotionDataSource]:
        return [ds async for ds in self._query_service.search_data_sources_stream(query)]

    async def search_data_sources_stream(self, query: str) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.search_data_sources_stream(query):
            yield data_source

    async def get_pages(self) -> list[NotionPage]:
        return [page async for page in self._query_service.get_pages_stream()]

    async def get_pages_stream(self) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.get_pages_stream():
            yield page

    async def search_pages(self, query: str) -> list[NotionPage]:
        return [page async for page in self._query_service.search_pages_stream(query)]

    async def search_pages_stream(self, query: str) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.search_pages_stream(query):
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
