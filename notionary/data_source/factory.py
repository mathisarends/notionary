from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.http.data_source_client import DataSourceClient
from notionary.data_source.schemas import DataSourceDto
from notionary.shared.entity.utils import extract_parent_database
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType
from notionary.workspace.search.search_client import SearchClient

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource


class DataSourceFactory:
    def __init__(
        self,
        data_source_client: DataSourceClient | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
        search_client: SearchClient | None = None,
    ) -> None:
        self._data_source_client = data_source_client or DataSourceClient()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()
        self._search_client = search_client or SearchClient()

    async def load_from_id(self, data_source_id: str) -> NotionDataSource:
        data_source_dto = await self._data_source_client.get_data_source(data_source_id)
        return await self._create_from_response(data_source_dto)

    async def load_from_title(self, data_source_title: str, min_similarity: float = 0.6) -> NotionDataSource:
        return await self._search_client.find_data_source(data_source_title, min_similarity=min_similarity)

    async def _create_from_response(self, response: DataSourceDto) -> NotionDataSource:
        from notionary.data_source.service import NotionDataSource

        title, description, parent_database = await asyncio.gather(
            self._extract_title(response),
            self._extract_description(response),
            extract_parent_database(response),
        )

        return NotionDataSource(
            id=response.id,
            title=title,
            description=description,
            created_time=response.created_time,
            last_edited_time=response.last_edited_time,
            archived=response.archived,
            in_trash=response.in_trash,
            properties=response.properties,
            parent_database=parent_database,
            emoji_icon=self._extract_emoji_icon(response),
            external_icon_url=self._extract_external_icon_url(response),
            cover_image_url=self._extract_cover_image_url(response),
        )

    async def _extract_title(self, response: DataSourceDto) -> str:
        return await self._rich_text_markdown_converter.to_markdown(response.title)

    async def _extract_description(self, response: DataSourceDto) -> str | None:
        if not response.description:
            return None
        return await self._rich_text_markdown_converter.to_markdown(response.description)

    def _extract_emoji_icon(self, response: DataSourceDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EMOJI:
            return None
        return response.icon.emoji

    def _extract_external_icon_url(self, response: DataSourceDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EXTERNAL:
            return None
        return response.icon.external.url if response.icon.external else None

    def _extract_cover_image_url(self, response: DataSourceDto) -> str | None:
        if not response.cover or response.cover.type != CoverType.EXTERNAL:
            return None
        return response.cover.external.url if response.cover.external else None


async def load_data_source_from_id(data_source_id: str) -> NotionDataSource:
    factory = DataSourceFactory()
    return await factory.load_from_id(data_source_id)


async def load_data_source_from_title(title: str, min_similarity: float = 0.6) -> NotionDataSource:
    factory = DataSourceFactory()
    return await factory.load_from_title(title, min_similarity=min_similarity)
