# notionary/page/page_factory.py
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import convert_rich_text_to_markdown
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.entity.factory.parent_extract_mixin import ParentExtractMixin
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType
from notionary.workspace.search.search_client import SearchClient

if TYPE_CHECKING:
    from notionary import NotionPage


class NotionPageFactory(ParentExtractMixin):
    async def load_from_id(self, page_id: str) -> NotionPage:
        response = await self._fetch_page_response(page_id)
        return await self._create_page_from_response(response)

    async def load_from_title(self, page_title: str, min_similarity: float = 0.6) -> NotionPage:
        search_client = SearchClient()
        return await search_client.find_page(page_title, min_similarity=min_similarity)

    async def _fetch_page_response(self, page_id: str) -> NotionPageDto:
        async with NotionPageHttpClient(page_id=page_id) as client:
            return await client.get_page()

    async def _create_page_from_response(self, response: NotionPageDto) -> NotionPage:
        from notionary import NotionPage

        title, parent_data_source = await asyncio.gather(
            self._extract_title(response),
            self._extract_parent_data_source(response),
        )

        return NotionPage(
            id=response.id,
            title=title,
            created_time=response.created_time,
            last_edited_time=response.last_edited_time,
            archived=response.archived,
            in_trash=response.in_trash,
            url=response.url,
            parent_type=response.parent.type,
            public_url=response.public_url,
            properties=response.properties,
            parent_data_source=parent_data_source,
            emoji_icon=self._extract_emoji_icon(response),
            external_icon_url=self._extract_external_icon_url(response),
            cover_image_url=self._extract_cover_image_url(response),
        )

    async def _extract_title(self, response: NotionPageDto) -> str:
        title_property = self._find_title_property(response)
        rich_text_title = title_property.title if title_property else []
        return await convert_rich_text_to_markdown(rich_text_title)

    def _find_title_property(self, response: NotionPageDto) -> PageTitleProperty | None:
        return next(
            (prop for prop in response.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )

    def _extract_emoji_icon(self, response: NotionPageDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EMOJI:
            return None
        return response.icon.emoji

    def _extract_external_icon_url(self, response: NotionPageDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EXTERNAL:
            return None
        return response.icon.external.url if response.icon.external else None

    def _extract_cover_image_url(self, response: NotionPageDto) -> str | None:
        if not response.cover or response.cover.type != CoverType.EXTERNAL:
            return None
        return response.cover.external.url if response.cover.external else None


async def load_page_from_id(page_id: str) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_id(page_id)


async def load_page_from_title(title: str, min_similarity: float = 0.6) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_title(title, min_similarity)
