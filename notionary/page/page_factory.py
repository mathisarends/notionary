from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.page.page_client import NotionPageClient
from notionary.page.page_models import NotionPageResponse
from notionary.util import extract_uuid, format_uuid
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionPage


async def load_page_from_id(page_id: str, token: str | None = None) -> NotionPage:
    """Load a NotionPage from a page ID."""
    formatted_id = format_uuid(page_id) or page_id

    async with NotionPageClient(token=token) as client:
        page_response = await client.get_page(formatted_id)
        return await _load_page_from_response(page_response, token)


async def load_page_from_name(
    page_name: str, token: str | None = None, min_similarity: float = 0.6
) -> NotionPage:
    """Load a NotionPage by finding a page with fuzzy matching on the title."""
    # Lazy import to avoid circular imports
    from notionary.workspace import NotionWorkspace

    workspace = NotionWorkspace()

    search_results: list[NotionPage] = await workspace.search_pages(page_name, limit=5)

    if not search_results:
        raise ValueError(f"No pages found for name: {page_name}")

    best_match = find_best_match(
        query=page_name,
        items=search_results,
        text_extractor=lambda page: page.title,
        min_similarity=min_similarity,
    )

    if not best_match:
        available_titles = [result.title for result in search_results[:5]]
        raise ValueError(
            f"No sufficiently similar page found for '{page_name}'. "
            f"Available: {available_titles}"
        )

    async with NotionPageClient(token=token) as client:
        page_response = await client.get_page(page_id=best_match.item.id)
        return await _load_page_from_response(page_response=page_response, token=token)


async def load_page_from_url(url: str, token: str | None = None) -> NotionPage:
    """Load a NotionPage from a Notion page URL."""
    page_id = extract_uuid(url)
    if not page_id:
        raise ValueError(f"Could not extract page ID from URL: {url}")

    formatted_id = format_uuid(page_id) or page_id

    async with NotionPageClient(token=token) as client:
        page_response = await client.get_page(formatted_id)
        return await _load_page_from_response(page_response, token)


async def _load_page_from_response(
    page_response: NotionPageResponse,
    token: str | None,
) -> NotionPage:
    """Create NotionPage instance from API response."""
    # Lazy import to avoid circular imports
    from notionary import NotionPage
    from notionary.database.database import NotionDatabase

    title = _extract_title(page_response)
    emoji_icon = _extract_page_emoji_icon(page_response)
    external_icon_url = _extract_external_icon_url(page_response)
    cover_image_url = _extract_cover_image_url(page_response)
    parent_database_id = _extract_parent_database_id(page_response)

    parent_database = (
        await NotionDatabase.from_database_id(id=parent_database_id, token=token)
        if parent_database_id
        else None
    )

    return NotionPage(
        page_id=page_response.id,
        title=title,
        url=page_response.url,
        emoji_icon=emoji_icon,
        external_icon_url=external_icon_url,
        cover_image_url=cover_image_url,
        archived=page_response.archived,
        in_trash=page_response.in_trash,
        properties=page_response.properties,
        parent_database=parent_database,
        token=token,
    )


def _extract_title(page_response: NotionPageResponse) -> str:
    """Extract title from page response. Returns empty string if not found."""
    if not page_response.properties:
        return ""

    title_property = next(
        (
            prop
            for prop in page_response.properties.values()
            if isinstance(prop, dict) and prop.get("type") == "title"
        ),
        None,
    )

    if not title_property or "title" not in title_property:
        return ""

    try:
        title_parts = title_property["title"]
        return "".join(part.get("plain_text", "") for part in title_parts)
    except (KeyError, TypeError, AttributeError):
        return ""


def _extract_page_emoji_icon(page_response: NotionPageResponse) -> str | None:
    """Extract emoji icon from page response."""
    if not page_response.icon:
        return None

    if page_response.icon.type == "emoji":
        return page_response.icon.emoji


def _extract_external_icon_url(page_response: NotionPageResponse) -> str | None:
    """Extract external icon URL from page response."""
    if not page_response.icon:
        return None

    if page_response.icon.type == "external":
        return page_response.icon.external.url


def _extract_parent_database_id(page_response: NotionPageResponse) -> str | None:
    """Extract parent database ID from page response."""
    parent = page_response.parent

    if not parent:
        return

    if parent.type == "database_id":
        return parent.database_id


def _extract_cover_image_url(page_response: NotionPageResponse) -> str | None:
    """Extract cover image URL from page response."""
    if not page_response.cover:
        return None

    if page_response.cover.type == "external":
        return page_response.cover.external.url
