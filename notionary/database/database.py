from collections.abc import Awaitable, Callable

from notionary.data_source.data_source import DataSource
from notionary.database.client import DatabaseHttpClient
from notionary.database.schemas import DatabaseDto
from notionary.http.client import HttpClient
from notionary.shared.entity.cover import EntityCover
from notionary.shared.entity.icon import EntityIcon
from notionary.shared.entity.trash import EntityTrash

type _DataSourceFactory = Callable[[str], Awaitable[DataSource]]


# TODO: Title und Description hier mit einer async api abfragen bitte (den database http client hierfür haben wir ja schon dann)
class Database:
    def __init__(
        self,
        dto: DatabaseDto,
        http: HttpClient,
    ) -> None:
        self.metadata: DatabaseDto = dto

        path = f"databases/{dto.id}"
        self._icon = EntityIcon(dto, http, path)
        self._cover = EntityCover(dto, http, path)
        self._trash = EntityTrash(dto, http, path)

        self.is_inline = dto.is_inline
        self._client = DatabaseHttpClient(http=http)

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def title(self) -> str:
        return "".join(rt.plain_text for rt in self.metadata.title)

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
