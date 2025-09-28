from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageTitleProperty
from notionary.shared.entity.factory.entity_factory import EntityFactory
from notionary.shared.entity.factory.parent_extract_mixin import ParentExtractMixin
from notionary.workspace.search.search_client import SearchClient

if TYPE_CHECKING:
    from notionary import NotionPage

    BaseFactory = EntityFactory[NotionPage]
else:
    BaseFactory = EntityFactory


class NotionPageFactory(BaseFactory, ParentExtractMixin):
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

        entity_kwargs = self._create_common_entity_kwargs(response)

        title, parent_database, parent_data_source = await asyncio.gather(
            self._extract_title(response),
            self._extract_parent_database(response),
            self._extract_parent_data_source(response),
        )

        entity_kwargs.update(
            {
                "title": title,
                "created_time": response.created_time,
                "last_edited_time": response.last_edited_time,
                "archived": response.archived,
                "url": response.url,
                "public_url": response.public_url,
                "properties": response.properties,
            }
        )

        entity_kwargs["parent_database"] = parent_database
        entity_kwargs["parent_data_source"] = parent_data_source
        return NotionPage(**entity_kwargs)

    async def _extract_title(self, response: NotionPageDto) -> str:
        title_property = self._lookup_title_property_in_page_response(response)
        rich_text_title = title_property.title if title_property else []
        return await self._extract_title_from_rich_text_objects(rich_text_title)

    def _lookup_title_property_in_page_response(self, response: NotionPageDto) -> PageTitleProperty | None:
        return next(
            (prop for prop in response.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )

    async def _extract_title_from_rich_text_objects(self, rich_text_objects: list[RichTextObject]) -> str:
        rich_text_markdown_converter = RichTextToMarkdownConverter()
        title = await rich_text_markdown_converter.to_markdown(rich_text_objects)
        return title


async def load_page_from_id(page_id: str) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_id(page_id)


async def load_page_from_title(title: str, min_similarity: float = 0.6) -> NotionPage:
    factory = NotionPageFactory()
    return await factory.load_from_title(title, min_similarity)
