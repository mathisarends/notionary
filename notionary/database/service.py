import asyncio
from collections.abc import Awaitable, Callable

from notionary.data_source.data_source import DataSource
from notionary.database.client import DatabaseHttpClient
from notionary.database.database_metadata_update_client import (
    DatabaseMetadataUpdateClient,
)
from notionary.database.schemas import DatabaseDto
from notionary.shared.entity.service import Entity

type _DataSourceFactory = Callable[[str], Awaitable[DataSource]]


class Database(Entity):
    def __init__(
        self,
        dto: DatabaseDto,
        title: str,
        description: str | None,
        data_source_ids: list[str],
        client: DatabaseHttpClient,
        metadata_update_client: DatabaseMetadataUpdateClient,
    ) -> None:
        super().__init__(dto=dto)

        self.title = title
        self.description = description
        self.is_inline = dto.is_inline

        self._data_sources: list[DataSource] | None = None
        self._data_source_ids = data_source_ids

        self.client = client
        self.metadata_update_client = metadata_update_client

    def get_description(self) -> str | None:
        return self._description

    async def get_data_sources(
        self,
        data_source_factory: _DataSourceFactory = DataSource.from_id,
    ) -> list[DataSource]:
        if self._data_sources is None:
            self._data_sources = await self._load_data_sources(data_source_factory)
        return self._data_sources

    async def _load_data_sources(
        self,
        data_source_factory: _DataSourceFactory,
    ) -> list[DataSource]:
        tasks = [data_source_factory(ds_id) for ds_id in self._data_source_ids]
        return list(await asyncio.gather(*tasks))

    # async def set_title(self, title: str) -> None:
    #     rich_text = await converter.to_rich_text(title)
    #     result = await self.client.update_database_title(rich_text)
    #     self._title = result.title[0].plain_text if result.title else ""

    # async def set_description(self, description: str) -> None:
    #     md_to_rt = create_markdown_rich_text_converter()
    #     rich_text = await md_to_rt.to_rich_text(description)
    #     result = await self.client.update_database_description(rich_text)
    #     rt_to_md = RichTextToMarkdownConverter()
    #     self._description = await rt_to_md.to_markdown(result.description)
