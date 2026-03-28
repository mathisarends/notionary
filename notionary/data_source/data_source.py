import logging
from uuid import UUID

from notionary.data_source.client import (
    DataSourceClient,
)
from notionary.data_source.properties.schemas import (
    AnyDataSourceProperty,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.entity.cover import EntityCover
from notionary.shared.entity.icon import EntityIcon
from notionary.shared.entity.trash import EntityTrash
from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon

logger = logging.getLogger(__name__)


class DataSource:
    def __init__(
        self,
        id: UUID,
        url: str,
        title: str,
        description: str | None,
        icon: Icon | None,
        cover: File | None,
        in_trash: bool,
        properties: dict[str, AnyDataSourceProperty],
        http: HttpClient,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.description = description

        path = f"data_sources/{id}"
        self._icon = EntityIcon(icon=icon, http_client=http, path=path)
        self._cover = EntityCover(cover=cover, http_client=http, path=path)
        self._trash = EntityTrash(in_trash=in_trash, http_client=http, path=path)

        self.properties = properties or {}
        self._client = DataSourceClient(http=http, data_source_id=id)

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

    async def set_title(self, title: str) -> None:
        dto = await self._client.set_title(title)
        title_markdown = rich_text_to_markdown(dto.title)
        self.title = title_markdown

    async def create_page(self, title: str | None = None) -> Page:
        return await self._client.create_page(title=title)
