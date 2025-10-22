import asyncio
from collections.abc import Awaitable, Callable
from typing import Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.service import NotionDataSource
from notionary.database.client import NotionDatabaseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.database.schemas import NotionDatabaseDto
from notionary.shared.entity.dto_parsers import (
    extract_description,
    extract_title,
)
from notionary.shared.entity.service import Entity
from notionary.workspace.query.service import WorkspaceQueryService

type _DataSourceFactory = Callable[[str], Awaitable[NotionDataSource]]


class NotionDatabase(Entity):
    def __init__(
        self,
        dto: NotionDatabaseDto,
        title: str,
        description: str | None,
        data_source_ids: list[str],
        client: NotionDatabaseHttpClient,
        metadata_update_client: DatabaseMetadataUpdateClient,
    ) -> None:
        super().__init__(dto=dto)

        self._title = title
        self._description = description
        self._is_inline = dto.is_inline

        self._data_sources: list[NotionDataSource] | None = None
        self._data_source_ids = data_source_ids

        self.client = client
        self._metadata_update_client = metadata_update_client

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
        search_service: WorkspaceQueryService | None = None,
    ) -> Self:
        service = search_service or WorkspaceQueryService()
        return await service.find_database(database_title)

    @classmethod
    async def _create_from_dto(
        cls,
        dto: NotionDatabaseDto,
        rich_text_converter: RichTextToMarkdownConverter,
        client: NotionDatabaseHttpClient,
    ) -> Self:
        title, description = await asyncio.gather(
            extract_title(dto, rich_text_converter), extract_description(dto, rich_text_converter)
        )

        metadata_update_client = DatabaseMetadataUpdateClient(database_id=dto.id)

        return cls(
            dto=dto,
            title=title,
            description=description,
            data_source_ids=[ds.id for ds in dto.data_sources],
            client=client,
            metadata_update_client=metadata_update_client,
        )

    @property
    def _entity_metadata_update_client(self) -> DatabaseMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def is_inline(self) -> bool:
        return self._is_inline

    def get_description(self) -> str | None:
        return self._description

    async def get_data_sources(
        self,
        data_source_factory: _DataSourceFactory = NotionDataSource.from_id,
    ) -> list[NotionDataSource]:
        if self._data_sources is None:
            self._data_sources = await self._load_data_sources(data_source_factory)
        return self._data_sources

    async def _load_data_sources(
        self,
        data_source_factory: _DataSourceFactory,
    ) -> list[NotionDataSource]:
        tasks = [data_source_factory(ds_id) for ds_id in self._data_source_ids]
        return list(await asyncio.gather(*tasks))

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text if result.title else ""

    async def set_description(self, description: str) -> None:
        updated_description = await self.client.update_database_description(description=description)
        self._description = updated_description
