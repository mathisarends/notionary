from collections.abc import AsyncIterator

from notionary.database.exceptions import DatabaseNotFound
from notionary.database.factory import DatabaseFactory
from notionary.database.schemas import (
    DatabaseDto,
    DatabaseQueryConfig,
    SortDirection,
    SortTimestamp,
)
from notionary.database.service import Database
from notionary.http.client import HttpClient
from notionary.shared.fuzzy import fuzzy_suggestions


class DatabaseNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._factory = DatabaseFactory(http)

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
        config = DatabaseQueryConfig(
            query=query,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            page_size=page_size,
            total_results_limit=total_results_limit,
        )
        async for item in self._http.paginate_stream(
            endpoint="search",
            total_results_limit=config.total_results_limit,
            **config.model_dump(),
        ):
            dto = DatabaseDto.model_validate(item)
            yield await self._factory.from_id(dto.id)

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
        return await self._factory.from_id(database_id)
