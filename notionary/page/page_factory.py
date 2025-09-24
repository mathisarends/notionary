from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.entities.entity_factory import NotionEntityFactory
from notionary.shared.entities.entity_models import NotionEntityResponseDto
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionPage


class NotionPageFactory(NotionEntityFactory):
    async def load_from_id(self, page_id: str) -> NotionPage:
        response = await self._fetch_page_response(page_id)
        return await self._create_page_from_response(response)

    async def load_from_title(self, page_title: str, min_similarity: float = 0.6) -> NotionPage:
        from notionary.workspace import NotionWorkspace

        workspace = NotionWorkspace()
        search_results = await workspace.search_pages(page_title, limit=10)

        if not search_results:
            raise ValueError(f"No pages found for name: {page_title}")

        best_match = find_best_match(
            query=page_title,
            items=search_results,
            text_extractor=lambda page: page.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in search_results[:5]]
            raise ValueError(f"No sufficiently similar page found for '{page_title}'. Available: {available_titles}")

        return await self.load_from_id(best_match.item.id)

    async def _extract_title(self, response: NotionEntityResponseDto) -> str:
        title_property = self._lookup_title_property_in_page_response(response)
        rich_text_title = title_property.title if title_property else []
        return await self._extract_title_from_rich_text_objects(rich_text_title)

    async def _fetch_page_response(self, page_id: str) -> NotionEntityResponseDto:
        from notionary.page.page_http_client import NotionPageHttpClient

        async with NotionPageHttpClient(page_id=page_id) as client:
            return await client.get_page()

    async def _create_page_from_response(self, response: NotionEntityResponseDto) -> NotionPage:
        from notionary import NotionDatabase, NotionPage

        entity_kwargs = await self._create_common_entity_kwargs(response)

        parent_database = None
        parent_db_id = self._extract_parent_database_id(response)
        if parent_db_id:
            parent_database = await NotionDatabase.from_id(parent_db_id)

        entity_kwargs["parent_database"] = parent_database
        return NotionPage(**entity_kwargs)

    def _lookup_title_property_in_page_response(self, response: NotionEntityResponseDto) -> PageTitleProperty | None:
        return next(
            (prop for prop in response.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )


async def load_page_from_id(page_id: str) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_id(page_id)


async def load_page_from_title(page_title: str, min_similarity: float = 0.6) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_title(page_title, min_similarity)
