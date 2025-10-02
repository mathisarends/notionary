from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.database.models import NotionDatabaseDto
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType
from notionary.workspace.search.search_client import SearchClient

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionDatabaseFactory:
    def __init__(
        self,
        search_client: SearchClient | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        self._search_client = search_client or SearchClient()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    async def load_from_id(self, database_id: str) -> NotionDatabase:
        response_dto = await self._fetch_database_response(database_id)
        return await self._create_database_from_response(response_dto)

    async def load_from_title(self, database_title: str) -> NotionDatabase:
        async with self._search_client as data_source_client:
            return await data_source_client.find_database(database_title)

    async def _fetch_database_response(self, database_id: str) -> NotionDatabaseDto:
        from notionary.database.database_http_client import NotionDatabaseHttpClient

        async with NotionDatabaseHttpClient(database_id=database_id) as client:
            return await client.get_database()

    async def _create_database_from_response(self, response: NotionDatabaseDto) -> NotionDatabase:
        from notionary import NotionDatabase

        title = await self._extract_title(response)
        description = await self._extract_description(response)

        return NotionDatabase(
            id=str(response.id),
            title=title,
            description=description,
            created_time=response.created_time,
            last_edited_time=response.last_edited_time,
            in_trash=response.in_trash,
            is_inline=response.is_inline,
            url=response.url,
            public_url=response.public_url,
            emoji_icon=self._extract_emoji_icon(response),
            external_icon_url=self._extract_external_icon_url(response),
            cover_image_url=self._extract_cover_image_url(response),
            data_source_ids=[ds.id for ds in response.data_sources],
        )

    def _extract_emoji_icon(self, response: NotionDatabaseDto) -> str | None:
        if response.icon and response.icon.type == IconType.EMOJI:
            return response.icon.emoji
        return None

    def _extract_external_icon_url(self, response: NotionDatabaseDto) -> str | None:
        if response.icon and response.icon.type == IconType.EXTERNAL and response.icon.external:
            return response.icon.external.url
        return None

    def _extract_cover_image_url(self, response: NotionDatabaseDto) -> str | None:
        if response.cover and response.cover.type == CoverType.EXTERNAL and response.cover.external:
            return response.cover.external.url
        return None

    async def _extract_title(self, response: NotionDatabaseDto) -> str:
        return await self._rich_text_markdown_converter.to_markdown(response.title)

    async def _extract_description(self, response: NotionDatabaseDto) -> str:
        return await self._rich_text_markdown_converter.to_markdown(response.description)


async def load_database_from_id(database_id: str) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_id(database_id)


async def load_database_from_title(database_title: str) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_title(database_title)
