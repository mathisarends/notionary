from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.database.database_models import NoionDatabaseDto
from notionary.shared.models.icon_models import IconType
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionDatabase


async def load_database_from_id(database_id: str) -> NotionDatabase:
    """Load a NotionDatabase from a database ID."""
    formatted_id = format_uuid(database_id) or database_id

    async with NotionDatabseHttpClient(database_id=formatted_id) as client:
        db_response = await client.get_database()
        return _load_database_from_response(db_response)


async def load_database_from_name(database_name: str, min_similarity: float = 0.6) -> NotionDatabase:
    """Load a NotionDatabase by finding a database with fuzzy matching on the title."""
    from notionary.workspace import NotionWorkspace

    workspace = NotionWorkspace()
    search_results: list[NotionDatabase] = await workspace.search_databases(database_name, limit=10)

    if not search_results:
        raise ValueError(f"No databases found for name: {database_name}")

    best_match = find_best_match(
        query=database_name,
        items=search_results,
        text_extractor=lambda database: database.title,
        min_similarity=min_similarity,
    )

    if not best_match:
        available_titles = [result.title for result in search_results[:5]]
        raise ValueError(f"No sufficiently similar database found for '{database_name}'. Available: {available_titles}")

    async with NotionDatabseHttpClient(database_id=best_match.item.id) as client:
        db_response = await client.get_database()
        return _load_database_from_response(db_response=db_response)


def _load_database_from_response(
    db_response: NoionDatabaseDto,
) -> NotionDatabase:
    """Create NotionDatabase instance from API response with typed properties."""
    from notionary import NotionDatabase

    title = _extract_title(db_response)
    emoji_icon = _extract_emoji_icon(db_response)

    return NotionDatabase(
        id=db_response.id,
        title=title,
        url=db_response.url,
        emoji_icon=emoji_icon,
        properties=db_response.properties,
    )


def _extract_title(db_response: NoionDatabaseDto) -> str:
    """Extract title from database response."""
    if db_response.title and len(db_response.title) > 0:
        return db_response.title[0].plain_text
    return "Untitled Database"


def _extract_emoji_icon(db_response: NoionDatabaseDto) -> str | None:
    """Extract emoji icon from database response."""
    if not db_response.icon:
        return None

    if db_response.icon.type == IconType.EMOJI:
        return db_response.icon.emoji

    return None
