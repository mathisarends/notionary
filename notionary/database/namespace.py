import logging
from dataclasses import dataclass

from notionary.database.client import DatabaseHttpClient
from notionary.database.database import NotionDatabase
from notionary.http import HttpClient
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabasePage:
    items: list[NotionDatabase]
    has_more: bool
    next_cursor: str | None


class DatabasesNamespace:
    def __init__(
        self,
        http: HttpClient,
        rich_text_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        self._client = DatabaseHttpClient(http)
        self._converter = rich_text_converter or RichTextToMarkdownConverter()

    async def get(self, database_id: str) -> NotionDatabase:
        """Fetch a database by its ID."""
        dto = await self._client.get(database_id)
        return await NotionDatabase.from_dto(dto, self._client, self._converter)

    async def search(self, query: str = "") -> list[NotionDatabase]:
        databases: list[NotionDatabase] = []
        cursor: str | None = None

        while True:
            page = await self._fetch_page(query=query, start_cursor=cursor)
            databases.extend(page.items)
            if not page.has_more:
                break
            cursor = page.next_cursor

        logger.debug("search(%r) → %d databases", query, len(databases))
        return databases

    async def list(
        self,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> DatabasePage:
        """Fetch a single page of databases (caller controls pagination)."""
        return await self._fetch_page(
            query="", start_cursor=start_cursor, page_size=page_size
        )

    async def find_by_title(self, title: str) -> NotionDatabase:
        """Find the first database whose title matches *title* (case-insensitive).

        Raises ``ValueError`` when no match is found.
        """
        title_lower = title.lower()
        results = await self.search(query=title)

        for db in results:
            if db.title.lower() == title_lower:
                return db

        raise ValueError(
            f"No database found with title {title!r}. "
            f"Found: {[db.title for db in results] or '(none)'}"
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _fetch_page(
        self,
        query: str = "",
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> DatabasePage:
        response = await self._client.search(
            query=query,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        items = [
            await NotionDatabase.from_dto(dto, self._client, self._converter)
            for dto in response.results
        ]
        return DatabasePage(
            items=items,
            has_more=response.has_more,
            next_cursor=response.next_cursor,
        )
