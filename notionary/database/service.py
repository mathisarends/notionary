from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.service import NotionDataSource
from notionary.database.client import NotionDatabaseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.database.schemas import NotionDatabaseDto
from notionary.shared.entity.dto_parsers import (
    extract_cover_image_url_from_dto,
    extract_description,
    extract_emoji_icon_from_dto,
    extract_external_icon_url_from_dto,
    extract_title,
)
from notionary.shared.entity.service import Entity
from notionary.user.schemas import PartialUserDto
from notionary.workspace.search.search_client import SearchClient

type DataSourceFactory = Callable[[str], Awaitable[NotionDataSource]]


class NotionDatabase(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        url: str,
        in_trash: bool,
        is_inline: bool,
        data_source_ids: list[str],
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        client: NotionDatabaseHttpClient | None = None,
        metadata_update_client: DatabaseMetadataUpdateClient | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
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

        self.client = client or NotionDatabaseHttpClient(database_id=id)
        self._metadata_update_client = metadata_update_client or DatabaseMetadataUpdateClient(database_id=id)

    @classmethod
    async def from_id(
        cls,
        database_id: str,
        rich_text_converter: RichTextToMarkdownConverter | None = None,
        database_client: NotionDatabaseHttpClient | None = None,
    ) -> Self:
        converter = rich_text_converter or RichTextToMarkdownConverter()
        client = database_client or NotionDatabaseHttpClient(database_id=database_id)

        async with client:
            response_dto = await client.get_database()

        return await cls._create_from_dto(response_dto, converter, client)

    @classmethod
    async def from_title(
        cls,
        database_title: str,
        min_similarity: float = 0.6,
        search_client: SearchClient | None = None,
    ) -> Self:
        client = search_client or SearchClient()
        async with client:
            return await client.find_database(database_title, min_similarity=min_similarity)

    @classmethod
    async def _create_from_dto(
        cls,
        response: NotionDatabaseDto,
        rich_text_converter: RichTextToMarkdownConverter,
        client: NotionDatabaseHttpClient,
    ) -> Self:
        title_coroutine = extract_title(response, rich_text_converter)
        description_coroutine = extract_description(response, rich_text_converter)
        title, description = await asyncio.gather(title_coroutine, description_coroutine)

        return cls(
            id=response.id,
            title=title,
            description=description,
            created_time=response.created_time,
            created_by=response.created_by,
            last_edited_time=response.last_edited_time,
            last_edited_by=response.last_edited_by,
            in_trash=response.in_trash,
            is_inline=response.is_inline,
            url=response.url,
            public_url=response.public_url,
            emoji_icon=extract_emoji_icon_from_dto(response),
            external_icon_url=extract_external_icon_url_from_dto(response),
            cover_image_url=extract_cover_image_url_from_dto(response),
            data_source_ids=[ds.id for ds in response.data_sources],
            client=client,
        )

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

    def get_description(self) -> str | None:
        return self._description

    async def get_data_sources(
        self,
        data_source_factory: DataSourceFactory = NotionDataSource.from_id,
    ) -> list[NotionDataSource]:
        if self._data_sources is None:
            self._data_sources = await self._load_data_sources(data_source_factory)
        return self._data_sources

    async def _load_data_sources(
        self,
        data_source_factory: DataSourceFactory,
    ) -> list[NotionDataSource]:
        tasks = [data_source_factory(ds_id) for ds_id in self._data_source_ids]
        return list(await asyncio.gather(*tasks))

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text if result.title else ""

    async def set_description(self, description: str) -> None:
        updated_description = await self.client.update_database_description(description=description)
        self._description = updated_description
