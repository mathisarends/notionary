import asyncio
from collections.abc import Awaitable, Callable

from notionary.data_source.data_source import DataSource
from notionary.database.client import DatabaseHttpClient
from notionary.database.schemas import DatabaseDto
from notionary.http.client import HttpClient
from notionary.shared.entity.cover import EntityCover
from notionary.shared.entity.metadata import EntityMetadata
from notionary.shared.entity.trash import EntityTrash
from notionary.shared.icon.icon import EntityIcon

type _DataSourceFactory = Callable[[str], Awaitable[DataSource]]


class Database:
    def __init__(
        self,
        dto: DatabaseDto,
        title: str,
        description: str | None,
        data_source_ids: list[str],
        client: DatabaseHttpClient,
        http: HttpClient,
    ) -> None:
        self.metadata = EntityMetadata.from_dto(dto)

        path = f"databases/{dto.id}"
        self._icon = EntityIcon(dto, http, path)
        self._cover = EntityCover(dto, http, path)
        self._trash = EntityTrash(dto, http, path)

        self.title = title
        self.description = description
        self.is_inline = dto.is_inline

        self._data_sources: list[DataSource] | None = None
        self._data_source_ids = data_source_ids
        self._client = client

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def url(self) -> str:
        return self.metadata.url

    @property
    def in_trash(self) -> bool:
        return self._trash.in_trash

    async def trash(self) -> None:
        await self._trash.trash()

    async def restore(self) -> None:
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        await self._icon.set_from_url(url)

    async def remove_icon(self) -> None:
        await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        await self._cover.set_random_gradient()

    async def remove_cover(self) -> None:
        await self._cover.remove()

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
