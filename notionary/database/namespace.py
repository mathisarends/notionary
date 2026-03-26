from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from notionary.database.client import DatabaseHttpClient
from notionary.database.database import Database
from notionary.database.exceptions import DatabaseNotFound
from notionary.database.schemas import DatabaseDto
from notionary.database.search import (
    DatabaseSearchClient,
    SortDirection,
    SortTimestamp,
)
from notionary.http.client import HttpClient
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.fuzzy import fuzzy_suggestions


class DatabaseNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._client = DatabaseHttpClient(http)
        self._search_client = DatabaseSearchClient(http)

    async def list(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> list[Database]:
        return [
            db
            async for db in self.iter(
                query=query,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                page_size=page_size,
                total_results_limit=total_results_limit,
            )
        ]

    async def iter(
        self,
        query: str | None = None,
        sort_direction: SortDirection = SortDirection.DESCENDING,
        sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME,
        page_size: int = 100,
        total_results_limit: int | None = None,
    ) -> AsyncIterator[Database]:
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield self._database_from_dto(dto)

    async def search(self, query: str) -> list[Database]:
        return await self.list(query=query)

    async def from_title(self, title: str) -> Database:
        candidates = await self.list(query=title, page_size=100)

        exact = next(
            (db for db in candidates if db.title.lower() == title.lower()), None
        )
        if exact:
            return exact

        suggestions = fuzzy_suggestions(title, candidates)
        raise DatabaseNotFound(title, suggestions)

    async def from_id(self, database_id: str) -> Database:
        dto = await self._client.retrieve(database_id)
        return self._database_from_dto(dto)

    async def create(
        self,
        parent_page_id: str | None = None,
        title: str | None = None,
        description: str | None = None,
        is_inline: bool | None = None,
        initial_properties: dict[str, Any] | None = None,
        icon_emoji: str | None = None,
        cover_url: str | None = None,
    ) -> Database:
        dto = await self._client.create(
            parent_page_id=parent_page_id,
            title=title,
            description=description,
            is_inline=is_inline,
            initial_properties=initial_properties,
            icon_emoji=icon_emoji,
            cover_url=cover_url,
        )
        return self._database_from_dto(dto)

    def _database_from_dto(self, dto: DatabaseDto) -> Database:
        title = rich_text_to_markdown(dto.title)
        description_text = rich_text_to_markdown(dto.description)
        return Database(
            id=dto.id,
            url=dto.url,
            title=title,
            description=description_text if description_text else None,
            is_inline=dto.is_inline,
            is_locked=dto.is_locked,
            data_sources=dto.data_sources,
            icon=dto.icon,
            cover=dto.cover,
            in_trash=dto.in_trash,
            http=self._http,
        )
