import difflib
from collections.abc import AsyncIterator

from notionary.database.database import Database
from notionary.database.schemas import (
    DatabaseDto,
    DatabaseQueryConfig,
    SortDirection,
    SortTimestamp,
)
from notionary.exceptions.search import DatabaseNotFound
from notionary.http.client import HttpClient


def _fuzzy_suggestions(query: str, items: list[Database], top_n: int = 5) -> list[str]:
    scored = [
        (item, difflib.SequenceMatcher(None, query.lower(), item.title.lower()).ratio())
        for item in items
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [item.title for item, score in scored[:top_n] if score >= 0.6]


class DatabaseNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

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
            yield await Database.from_id(dto.id)

    async def search(self, query: str) -> list[Database]:
        return await self.list(query=query)

    async def from_title(self, title: str) -> Database:
        candidates = await self.list(query=title, page_size=100)

        exact = next(
            (db for db in candidates if db.title.lower() == title.lower()), None
        )
        if exact:
            return exact

        suggestions = _fuzzy_suggestions(title, candidates)
        raise DatabaseNotFound(title, suggestions)

    async def from_id(self, database_id: str) -> Database:
        return await Database.from_id(database_id)
