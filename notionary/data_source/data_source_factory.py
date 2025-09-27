from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.data_source_models import DataSourceDto, DataSourceSearchResponse
from notionary.data_source.http.data_source_client import DataSourceClient
from notionary.shared.entity.factory.entity_factory import EntityFactory
from notionary.shared.entity.factory.parent_extract_mixin import ParentExtractMixin
from notionary.util.fuzzy import find_best_match

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
    ) -> None:
        super().__init__()
        self._data_source_client = data_source_client or DataSourceClient()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    async def load_from_id(self, data_source_id: str) -> NotionDataSource:
        data_source_dto = await self._data_source_client.get_data_source(data_source_id)

        return await self._create_from_response(data_source_dto)

    async def load_from_title(self, data_source_title: str, min_similarity: float = 0.6) -> NotionDataSource:
        search_response = await self._data_source_client.search_data_sources(data_source_title)
        data_source_candidates = await self._extract_potential_data_sources_from_search_result(search_response)

        best_match = find_best_match(
            query=data_source_title,
            items=data_source_candidates,
            text_extractor=lambda data_source: data_source.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in data_source_candidates[:5]]
            raise ValueError(
                f"No sufficiently similar data source found for '{data_source_title}'. Available: {available_titles}"
            )

        return best_match.item

    async def _extract_potential_data_sources_from_search_result(
        self, search_response: DataSourceSearchResponse
    ) -> list[NotionDataSource]:
        from notionary.data_source.data_source import NotionDataSource

        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source.id) for data_source in search_response.results)
        )

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
