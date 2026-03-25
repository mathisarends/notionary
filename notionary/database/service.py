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

        self._title = title
        self._description = description
        self._is_inline = dto.is_inline

        self._data_sources: list[DataSource] | None = None
        self._data_source_ids = data_source_ids

        self.client = client
        self._metadata_update_client = metadata_update_client

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

    async def set_title(self, title: str) -> None:
        from notionary.rich_text.markdown_to_rich_text import (
            create_markdown_rich_text_converter,
        )

        converter = create_markdown_rich_text_converter()
        rich_text = await converter.to_rich_text(title)
        result = await self.client.update_database_title(rich_text)
        self._title = result.title[0].plain_text if result.title else ""

    async def set_description(self, description: str) -> None:
        from notionary.rich_text.markdown_to_rich_text import (
            create_markdown_rich_text_converter,
        )
        from notionary.rich_text.rich_text_to_markdown.converter import (
            RichTextToMarkdownConverter,
        )

        md_to_rt = create_markdown_rich_text_converter()
        rich_text = await md_to_rt.to_rich_text(description)
        result = await self.client.update_database_description(rich_text)
        rt_to_md = RichTextToMarkdownConverter()
        self._description = await rt_to_md.to_markdown(result.description)
