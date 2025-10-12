from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Self

from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource
    from notionary.page.service import NotionPage
    from notionary.user import BotUser, PersonUser


class NotionWorkspace:
    def __init__(self, name: str, file_upload_limit_in_bytes: int) -> None:
        self._name = name
        self._file_upload_limit_in_bytes = file_upload_limit_in_bytes
        self._query_service = WorkspaceQueryService()

    @property
    def name(self) -> str:
        return self._name

    @property
    def file_upload_limit_in_bytes(self) -> int:
        return self._file_upload_limit_in_bytes

    @classmethod
    async def from_current_integration(cls) -> Self: ...

    async def list_data_sources(self) -> list[NotionDataSource]:
        return await self._query_service.list_data_sources()

    async def list_data_sources_stream(self) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.list_data_sources_stream():
            yield data_source

    async def search_data_sources(self, query: str) -> list[NotionDataSource]:
        return await self._query_service.search_data_sources(query)

    async def search_data_sources_stream(self, query: str) -> AsyncIterator[NotionDataSource]:
        async for data_source in self._query_service.search_data_sources_stream(query):
            yield data_source

    async def list_pages(self) -> list[NotionPage]:
        return await self._query_service.list_pages()

    async def list_pages_stream(self) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.list_pages_stream():
            yield page

    async def search_pages(self, query: str) -> list[NotionPage]:
        return await self._query_service.search_pages(query)

    async def search_pages_stream(self, query: str) -> AsyncIterator[NotionPage]:
        async for page in self._query_service.search_pages_stream(query):
            yield page

    async def list_users(self) -> list[PersonUser]: ...

    async def list_users_stream(self) -> AsyncIterator[PersonUser]: ...

    async def list_bot_users(self) -> list[BotUser]: ...

    async def list_bot_users_stream(self) -> AsyncIterator[BotUser]: ...

    async def search_users(self, query: str) -> list[PersonUser]: ...

    async def search_users_stream(self, query: str) -> AsyncIterator[PersonUser]: ...
