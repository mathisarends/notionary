import logging
from pathlib import Path
from uuid import UUID

from notionary.data_source.client import (
    DataSourceClient,
)
from notionary.data_source.properties.schemas import (
    AnyDataSourceProperty,
)
from notionary.file_upload import FileUploads
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.object import Cover, Icon, Trash
from notionary.shared.object.icon.schemas import AnyIcon
from notionary.shared.object.schemas import File

logger = logging.getLogger(__name__)


class DataSource:
    """A Notion data source (database-like entity).

    Provides methods to manage metadata, icons, covers, trash state,
    and page creation.
    """

    def __init__(
        self,
        id: UUID,
        url: str,
        title: str,
        description: str | None,
        icon: AnyIcon | None,
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
        file_uploads = FileUploads(http)
        self._icon = Icon(
            icon=icon, http_client=http, path=path, file_uploads=file_uploads
        )
        self._cover = Cover(
            cover=cover, http_client=http, path=path, file_uploads=file_uploads
        )
        self._trash = Trash(in_trash=in_trash, http_client=http, path=path)

        self.properties = properties or {}
        self._client = DataSourceClient(http=http, data_source_id=id)

    @property
    def in_trash(self) -> bool:
        """Whether this data source is in the trash."""
        return self._trash.in_trash

    async def trash(self) -> None:
        """Move the data source to the trash."""
        await self._trash.trash()

    async def restore(self) -> None:
        """Restore the data source from the trash."""
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        """Set the data source icon to an emoji.

        Args:
            emoji: A single emoji character.
        """
        await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        """Set the data source icon to an external image URL.

        Args:
            url: Public URL of the image.
        """
        await self._icon.set_from_url(url)

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the data source icon.

        Args:
            file_path: Path to the image file.
        """
        await self._icon.set_from_file(file_path)

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the data source icon.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._icon.set_from_bytes(content, filename)

    async def remove_icon(self) -> None:
        """Remove the data source icon."""
        await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        """Set the data source cover to an external image URL.

        Args:
            url: Public URL of the cover image.
        """
        await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        """Set the data source cover to a random Notion gradient."""
        await self._cover.set_random_gradient()

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the data source cover.

        Args:
            file_path: Path to the image file.
        """
        await self._cover.set_from_file(file_path)

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the data source cover.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._cover.set_from_bytes(content, filename)

    async def remove_cover(self) -> None:
        """Remove the data source cover image."""
        await self._cover.remove()

    async def set_title(self, title: str) -> None:
        """Update the data source title.

        Args:
            title: New title.
        """
        dto = await self._client.set_title(title)
        title_markdown = rich_text_to_markdown(dto.title)
        self.title = title_markdown

    async def create_page(self, title: str | None = None) -> Page:
        """Create a new page inside this data source.

        Args:
            title: Optional page title.

        Returns:
            The newly created :class:`~notionary.page.page.Page`.
        """
        return await self._client.create_page(title=title)
