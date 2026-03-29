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
from notionary.shared.object import NotionObject
from notionary.shared.object.icon.schemas import AnyIcon
from notionary.shared.object.schemas import File
from notionary.user.schemas import PartialUserDto

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
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.description = description
        self.is_inline = is_inline
        self.is_locked = is_locked
        self.data_sources = data_sources
        self.created_time = created_time
        self.created_by = created_by
        self.last_edited_time = last_edited_time
        self.last_edited_by = last_edited_by

        path = f"databases/{id}"
        file_uploads = FileUploads(http)
        self._object = NotionObject(
            icon=icon,
            cover=cover,
            in_trash=in_trash,
            http_client=http,
            path=path,
            file_uploads=file_uploads,
        )

        self._client = DatabaseHttpClient(http)

    @property
    def in_trash(self) -> bool:
        """Whether this database is in the trash."""
        return self._object.in_trash

    async def trash(self) -> None:
        """Move the database to the trash."""
        await self._object.trash()

    async def restore(self) -> None:
        """Restore the database from the trash."""
        await self._object.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        """Set the database icon to an emoji.

        Args:
            emoji: A single emoji character.
        """
        await self._object.set_icon_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        """Set the database icon to an external image URL.

        Args:
            url: Public URL of the image.
        """
        await self._object.set_icon_url(url)

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the database icon.

        Args:
            file_path: Path to the image file.
        """
        await self._object.set_icon_from_file(file_path)

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the database icon.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._object.set_icon_from_bytes(content, filename)

    async def remove_icon(self) -> None:
        """Remove the database icon."""
        await self._object.remove_icon()

    async def set_cover(self, url: str) -> None:
        """Set the database cover to an external image URL.

        Args:
            url: Public URL of the cover image.
        """
        await self._object.set_cover_url(url)

    async def random_cover(self) -> None:
        """Set the database cover to a random Notion gradient."""
        await self._object.set_random_cover()

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the database cover.

        Args:
            file_path: Path to the image file.
        """
        await self._object.set_cover_from_file(file_path)

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the database cover.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._object.set_cover_from_bytes(content, filename)

    async def remove_cover(self) -> None:
        """Remove the database cover image."""
        await self._object.remove_cover()

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

    async def update(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        cover_url: str | None = None,
        is_locked: bool | None = None,
        is_inline: bool | None = None,
    ) -> None:
        """Update multiple database attributes in a single agent-friendly call.

        All parameters are optional — only provided values are applied.

        Args:
            title: New database title (supports inline markdown formatting).
            description: New database description (supports inline markdown formatting).
            icon_emoji: Emoji to set as the database icon.
            icon_url: External URL to set as the database icon.
            cover_url: External URL to set as the database cover.
            is_locked: If provided, lock or unlock the database.
            is_inline: If provided, toggle inline display mode.
        """
        if title is not None:
            await self.set_title(title)
        if description is not None:
            await self.set_description(description)
        await self._object.update(
            icon_emoji=icon_emoji,
            icon_url=icon_url,
            cover_url=cover_url,
        )
        if is_locked is not None:
            await self.lock() if is_locked else await self.unlock()
        if is_inline is not None:
            await self.set_inline(is_inline)

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"

    def __repr__(self) -> str:
        return f"Database(id={self.id!r}, title={self.title!r})"
