import logging
from pathlib import Path
from uuid import UUID

from notionary.database.client import DatabaseHttpClient
from notionary.database.schemas import (
    DataSourceReference,
    UpdateDatabaseRequest,
)
from notionary.file_upload import FileUploads
from notionary.http.client import HttpClient
from notionary.rich_text import markdown_to_rich_text, rich_text_to_markdown
from notionary.shared.object import Cover, Icon, Trash
from notionary.shared.object.icon.schemas import AnyIcon
from notionary.shared.object.schemas import File

logger = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        id: UUID,
        url: str,
        title: str,
        description: str | None,
        is_inline: bool,
        is_locked: bool,
        data_sources: list[DataSourceReference],
        icon: AnyIcon | None,
        cover: File | None,
        in_trash: bool,
        http: HttpClient,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.description = description
        self.is_inline = is_inline
        self.is_locked = is_locked
        self.data_sources = data_sources

        path = f"databases/{id}"
        file_uploads = FileUploads(http)
        self._icon = Icon(
            icon=icon, http_client=http, path=path, file_uploads=file_uploads
        )
        self._cover = Cover(
            cover=cover, http_client=http, path=path, file_uploads=file_uploads
        )
        self._trash = Trash(in_trash=in_trash, http_client=http, path=path)

        self._client = DatabaseHttpClient(http)

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

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        await self._icon.set_from_file(file_path)

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        await self._icon.set_from_bytes(content, filename)

    async def remove_icon(self) -> None:
        await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        await self._cover.set_random_gradient()

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        await self._cover.set_from_file(file_path)

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        await self._cover.set_from_bytes(content, filename)

    async def remove_cover(self) -> None:
        await self._cover.remove()

    async def set_title(self, title: str) -> None:
        rich = markdown_to_rich_text(title)
        dto = await self._client.update(self.id, UpdateDatabaseRequest(title=rich))
        self.title = rich_text_to_markdown(dto.title)

    async def set_description(self, description: str) -> None:
        rich = markdown_to_rich_text(description)
        dto = await self._client.update(
            self.id, UpdateDatabaseRequest(description=rich)
        )
        self.description = rich_text_to_markdown(dto.description)

    async def lock(self) -> None:
        dto = await self._client.update(self.id, UpdateDatabaseRequest(is_locked=True))
        self.is_locked = dto.is_locked

    async def unlock(self) -> None:
        dto = await self._client.update(self.id, UpdateDatabaseRequest(is_locked=False))
        self.is_locked = dto.is_locked

    async def set_inline(self, is_inline: bool) -> None:
        dto = await self._client.update(
            self.id, UpdateDatabaseRequest(is_inline=is_inline)
        )
        self.is_inline = dto.is_inline

    def __repr__(self) -> str:
        return f"Database(id={self.id!r}, title={self.title!r})"
