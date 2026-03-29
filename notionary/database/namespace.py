from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from notionary.database import mapper
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
from notionary.shared.search import fuzzy_suggestions


class DatabaseNamespace:
    """Scoped access to Notion databases.

    Provides listing, searching, creation, and retrieval of
    :class:`~notionary.database.database.Database` objects.
    """

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
        """Return databases as a list, optionally filtered by a search query.

        Args:
            query: Optional text query to filter databases by title.
            sort_direction: Sort order (ascending or descending).
            sort_timestamp: Sort by ``last_edited_time`` or ``created_time``.
            page_size: Number of results per API request.
            total_results_limit: Maximum total number of databases to return.

        Returns:
            A list of matching :class:`~notionary.database.database.Database` objects.
        """
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
        """Yield databases one by one without loading all results into memory.

        Accepts the same arguments as :meth:`list`.
        """
        async for dto in self._search_client.stream(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        ):
            yield self._database_from_dto(dto)

    async def search(self, query: str) -> list[Database]:
        """Search databases by title.

        Convenience alias for ``list(query=query)``.

        Args:
            query: Text query to match against database titles.
        """
        return await self.list(query=query)

    async def find(self, title: str) -> Database:
        """Find a database by its exact title (case-insensitive).

        Args:
            title: The database title to search for.

        Returns:
            The matching :class:`~notionary.database.database.Database`.

        Raises:
            DatabaseNotFound: If no exact match is found. The exception
                includes fuzzy suggestions when available.
        """
        candidates = await self.list(query=title, page_size=25, total_results_limit=25)

        exact = next(
            (db for db in candidates if db.title.lower() == title.lower()), None
        )
        if exact:
            return exact

        suggestions = fuzzy_suggestions(title, candidates)
        raise DatabaseNotFound(title, suggestions)

    async def from_id(self, database_id: UUID) -> Database:
        """Retrieve a database by its UUID.

        Args:
            database_id: The Notion database UUID.

        Returns:
            The :class:`~notionary.database.database.Database` for the given ID.
        """
        dto = await self._client.retrieve(database_id)
        return self._database_from_dto(dto)

    async def create(
        self,
        parent_page_id: UUID | None = None,
        title: str | None = None,
        description: str | None = None,
        is_inline: bool | None = None,
        initial_properties: dict[str, Any] | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        cover_url: str | None = None,
    ) -> Database:
        """Create a new database.

        Args:
            parent_page_id: UUID of the parent page. ``None`` for a
                top-level workspace database.
            title: Database title.
            description: Database description.
            is_inline: ``True`` to create as an inline database.
            initial_properties: Property schema definitions to include
                at creation time.
            icon_emoji: Emoji character to use as the icon.
            icon_url: External URL to use as the icon.
            cover_url: External URL for the cover image.

        Returns:
            The newly created :class:`~notionary.database.database.Database`.
        """
        dto = await self._client.create(
            parent_page_id=parent_page_id,
            title=title,
            description=description,
            is_inline=is_inline,
            initial_properties=initial_properties,
            icon_emoji=icon_emoji,
            icon_url=icon_url,
            cover_url=cover_url,
        )
        return self._database_from_dto(dto)

    def _database_from_dto(self, dto: DatabaseDto) -> Database:
        return mapper.to_database(dto, self._http)
