from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.database.database_models import NoionDatabaseDto
from notionary.shared.models.icon_models import IconType
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionDatabase


async def load_database_from_id(database_id: str, token: str | None = None) -> NotionDatabase:
    """Load a NotionDatabase from a database ID."""
    formatted_id = format_uuid(database_id) or database_id

    async with NotionDatabseHttpClient(token=token) as client:
        db_response = await client.get_database(formatted_id)
        return _load_database_from_response(db_response, token)


async def load_database_from_name(
    database_name: str, token: str | None = None, min_similarity: float = 0.6
) -> NotionDatabase:
    """Load a NotionDatabase by finding a database with fuzzy matching on the title."""
    async with NotionDatabseHttpClient(token=token) as client:
        search_result = await client.search_databases(database_name, limit=10)

        if not search_result.results:
            raise ValueError(f"No databases found for name: {database_name}")

        best_match = find_best_match(
            query=database_name,
            items=search_result.results,
            text_extractor=lambda db: _extract_title(db),
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [_extract_title(db) for db in search_result.results[:5]]
            raise ValueError(
                f"No sufficiently similar database found for '{database_name}'. Available: {available_titles}"
            )

        database_id = best_match.item.id
        db_response = await client.get_database(database_id=database_id)
        return _load_database_from_response(db_response, token)


def _load_database_from_response(
    db_response: NoionDatabaseDto,
    token: str | None,
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
        token=token,
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
