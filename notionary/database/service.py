from __future__ import annotations

import asyncio
from typing import Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.service import NotionDataSource
from notionary.database.database_http_client import NotionDatabaseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.database.models import NotionDatabaseDto
from notionary.shared.entity.entity import Entity
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType
from notionary.workspace.search.search_client import SearchClient


class NotionDatabase(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
        url: str,
        in_trash: bool,
        is_inline: bool,
        data_source_ids: list[str],
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            last_edited_time=last_edited_time,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._title = title
        self._url = url
        self._public_url = public_url
        self._description = description
        self._is_inline = is_inline

        self._data_sources: list[NotionDataSource] | None = None
        self._data_source_ids = data_source_ids

        self.client = NotionDatabaseHttpClient(database_id=id)

        self._metadata_update_client = DatabaseMetadataUpdateClient(database_id=id)

    @classmethod
    async def from_id(
        cls,
        database_id: str,
        rich_text_converter: RichTextToMarkdownConverter | None = None,
    ) -> Self:
        converter = rich_text_converter or RichTextToMarkdownConverter()
        response_dto = await cls._fetch_database_dto(database_id)
        return await cls._create_from_dto(response_dto, converter)

    @classmethod
    async def from_title(
        cls,
        database_title: str,
        search_client: SearchClient | None = None,
    ) -> Self:
        client = search_client or SearchClient()
        async with client:
            return await client.find_database(database_title)

    @classmethod
    async def _fetch_database_dto(cls, database_id: str) -> NotionDatabaseDto:
        async with NotionDatabaseHttpClient(database_id=database_id) as client:
            return await client.get_database()

    @classmethod
    async def _create_from_dto(
        cls,
        response: NotionDatabaseDto,
        rich_text_converter: RichTextToMarkdownConverter,
    ) -> Self:
        title = await cls._extract_title_from_dto(response, rich_text_converter)
        description = await cls._extract_description_from_dto(response, rich_text_converter)

        return cls(
            id=response.id,
            title=title,
            description=description,
            created_time=response.created_time,
            last_edited_time=response.last_edited_time,
            in_trash=response.in_trash,
            is_inline=response.is_inline,
            url=response.url,
            public_url=response.public_url,
            emoji_icon=cls._extract_emoji_icon_from_dto(response),
            external_icon_url=cls._extract_external_icon_url_from_dto(response),
            cover_image_url=cls._extract_cover_image_url_from_dto(response),
            data_source_ids=[ds.id for ds in response.data_sources],
        )

    @staticmethod
    async def _extract_title_from_dto(
        response: NotionDatabaseDto,
        rich_text_converter: RichTextToMarkdownConverter,
    ) -> str:
        return await rich_text_converter.to_markdown(response.title)

    @staticmethod
    async def _extract_description_from_dto(
        response: NotionDatabaseDto,
        rich_text_converter: RichTextToMarkdownConverter,
    ) -> str:
        return await rich_text_converter.to_markdown(response.description)

    @staticmethod
    def _extract_emoji_icon_from_dto(response: NotionDatabaseDto) -> str | None:
        if response.icon and response.icon.type == IconType.EMOJI:
            return response.icon.emoji
        return None

    @staticmethod
    def _extract_external_icon_url_from_dto(response: NotionDatabaseDto) -> str | None:
        if response.icon and response.icon.type == IconType.EXTERNAL and response.icon.external:
            return response.icon.external.url
        return None

    @staticmethod
    def _extract_cover_image_url_from_dto(response: NotionDatabaseDto) -> str | None:
        if response.cover and response.cover.type == CoverType.EXTERNAL and response.cover.external:
            return response.cover.external.url
        return None

    @property
    def _entity_metadata_update_client(self) -> DatabaseMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    @property
    def is_inline(self) -> bool:
        return self._is_inline

    async def get_data_sources(self) -> list[NotionDataSource]:
        if self._data_sources is None:
            self._data_sources = await self._load_data_sources()
        return self._data_sources

    async def _load_data_sources(self) -> list[NotionDataSource]:
        from notionary.data_source.service import NotionDataSource

        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source_id) for data_source_id in self._data_source_ids)
        )

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text

    async def set_description(self, description: str) -> None:
        updated_description = await self.client.update_database_description(description=description)
        self._description = updated_description

    def get_description(self) -> str | None:
        return self._description
