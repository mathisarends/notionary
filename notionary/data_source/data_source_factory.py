from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.data_source_models import DataSourceDto
from notionary.data_source.http.data_source_client import DataSourceClient
from notionary.shared.entity.factory.entity_factory import EntityFactory
from notionary.shared.entity.factory.parent_extract_mixin import ParentExtractMixin
from notionary.workspace.search.search_client import SearchClient

if TYPE_CHECKING:
    from notionary.data_source.data_source import NotionDataSource

    BaseFactory = EntityFactory[NotionDataSource]
else:
    BaseFactory = EntityFactory


class DataSourceFactory(BaseFactory, ParentExtractMixin):
    def __init__(
        self,
        data_source_client: DataSourceClient | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
        search_client: SearchClient | None = None,
    ) -> None:
        super().__init__()
        from notionary.workspace.search.search_client import SearchClient

        self._data_source_client = data_source_client or DataSourceClient()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()
        self._search_client = search_client or SearchClient()

    async def load_from_id(self, data_source_id: str) -> NotionDataSource:
        data_source_dto = await self._data_source_client.get_data_source(data_source_id)

        return await self._create_from_response(data_source_dto)

    async def load_from_title(self, data_source_title: str, min_similarity: float = 0.6) -> NotionDataSource:
        return await self._search_client.find_data_source(data_source_title, min_similarity=min_similarity)

    async def _create_from_response(self, data_source_dto: DataSourceDto) -> NotionDataSource:
        entity_kwargs = self._create_common_entity_kwargs(data_source_dto)

        title, description, parent_database = await asyncio.gather(
            self._extract_title(data_source_dto),
            self._extract_description(data_source_dto),
            self._extract_parent_database(data_source_dto),
        )

        entity_kwargs.update(
            {
                "title": title,
                "archived": data_source_dto.archived,
                "description": description,
                "properties": data_source_dto.properties,
                "parent_database": parent_database,
            }
        )

        return self._create_data_source_by_kwargs(**entity_kwargs)

    async def _extract_title(self, data_source_dto: DataSourceDto) -> str:
        rich_text_title = data_source_dto.title

        return await self._rich_text_markdown_converter.to_markdown(rich_text_title)

    async def _extract_description(self, data_source_dto: DataSourceDto) -> str | None:
        description_rich_text = data_source_dto.description

        if not description_rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(description_rich_text)

    def _create_data_source_by_kwargs(self, **kwargs) -> NotionDataSource:
        from notionary.data_source.data_source import NotionDataSource

        return NotionDataSource(**kwargs)


async def load_data_source_from_id(data_source_id: str) -> NotionDataSource:
    factory = DataSourceFactory()
    return await factory.load_from_id(data_source_id)


async def load_data_source_from_title(title: str) -> NotionDataSource:
    factory = DataSourceFactory()
    return await factory.load_from_title(title)
