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
    """A Notion database.

    Provides methods to manage metadata, icons, covers, and trash state
    of a database.
    """

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
        """Whether this database is in the trash."""
        return self._trash.in_trash

    async def trash(self) -> None:
        """Move the database to the trash."""
        await self._trash.trash()

    async def restore(self) -> None:
        """Restore the database from the trash."""
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        """Set the database icon to an emoji.

        Args:
            emoji: A single emoji character.
        """
        await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        """Set the database icon to an external image URL.

        Args:
            url: Public URL of the image.
        """
        await self._icon.set_from_url(url)

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the database icon.

        Args:
            file_path: Path to the image file.
        """
        await self._icon.set_from_file(file_path)

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the database icon.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._icon.set_from_bytes(content, filename)

    async def remove_icon(self) -> None:
        """Remove the database icon."""
        await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        """Set the database cover to an external image URL.

        Args:
            url: Public URL of the cover image.
        """
        await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        """Set the database cover to a random Notion gradient."""
        await self._cover.set_random_gradient()

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the database cover.

        Args:
            file_path: Path to the image file.
        """
        await self._cover.set_from_file(file_path)

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the database cover.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._cover.set_from_bytes(content, filename)

    async def remove_cover(self) -> None:
        """Remove the database cover image."""
        await self._cover.remove()

    async def set_title(self, title: str) -> None:
        """Update the database title.

        Args:
            title: New title (supports inline markdown formatting).
        """
        rich = markdown_to_rich_text(title)
        dto = await self._client.update(self.id, UpdateDatabaseRequest(title=rich))
        self.title = rich_text_to_markdown(dto.title)

    async def set_description(self, description: str) -> None:
        """Update the database description.

        Args:
            description: New description (supports inline markdown formatting).
        """
        rich = markdown_to_rich_text(description)
        dto = await self._client.update(
            self.id, UpdateDatabaseRequest(description=rich)
        )
        self.description = rich_text_to_markdown(dto.description)

    async def lock(self) -> None:
        """Lock the database to prevent editing."""
        dto = await self._client.update(self.id, UpdateDatabaseRequest(is_locked=True))
        self.is_locked = dto.is_locked

    async def unlock(self) -> None:
        """Unlock the database to allow editing."""
        dto = await self._client.update(self.id, UpdateDatabaseRequest(is_locked=False))
        self.is_locked = dto.is_locked

    async def set_inline(self, is_inline: bool) -> None:
        """Toggle whether the database is displayed inline.

        Args:
            is_inline: ``True`` for inline display, ``False`` for full-page.
        """
        dto = await self._client.update(
            self.id, UpdateDatabaseRequest(is_inline=is_inline)
        )
        self.is_inline = dto.is_inline

    def __repr__(self) -> str:
        return f"Database(id={self.id!r}, title={self.title!r})"
