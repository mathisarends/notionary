from pathlib import Path
from uuid import UUID

from notionary.file_upload import FileUploads
from notionary.http import HttpClient
from notionary.page.comments.service import PageComments
from notionary.page.content import PageContent
from notionary.page.properties import PageProperties
from notionary.page.properties.schemas import AnyPageProperty
from notionary.page.schemas import PageUpdateRequest, _DefaultTemplate, _TemplateById
from notionary.shared.object import NotionObject
from notionary.shared.object.icon.schemas import Icon
from notionary.shared.object.schemas import File
from notionary.user.schemas import PartialUserDto


class Page:
    """A Notion page.

    Provides methods to manage content, properties, icons, covers,
    comments, templates, and trash state of a single page.
    """

    def __init__(
        self,
        id: UUID,
        url: str,
        title: str,
        icon: Icon | None,
        cover: File | None,
        in_trash: bool,
        properties: dict[str, AnyPageProperty],
        http: HttpClient,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.created_time = created_time
        self.created_by = created_by
        self.last_edited_time = last_edited_time
        self.last_edited_by = last_edited_by

        path = f"pages/{id}"
        self._http = http
        self._path = path
        file_uploads = FileUploads(http)
        self._object = NotionObject(
            icon=icon,
            cover=cover,
            in_trash=in_trash,
            http_client=http,
            path=path,
            file_uploads=file_uploads,
        )

        self.properties = PageProperties(id=id, properties=properties, http=http)

        self._content = PageContent(page_id=id, http=http)
        self._comments = PageComments(page_id=id, http=http)

    @property
    def in_trash(self) -> bool:
        """Whether this page is in the trash."""
        return self._object.in_trash

    async def trash(self) -> None:
        """Move the page to the trash."""
        await self._object.trash()

    async def restore(self) -> None:
        """Restore the page from the trash."""
        await self._object.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        """Set the page icon to an emoji.

        Args:
            emoji: A single emoji character.
        """
        await self._object.set_icon_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        """Set the page icon to an external image URL.

        Args:
            url: Public URL of the image.
        """
        await self._object.set_icon_url(url)

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the page icon.

        Args:
            file_path: Path to the image file.
        """
        await self._object.set_icon_from_file(file_path)

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the page icon.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._object.set_icon_from_bytes(content, filename)

    async def remove_icon(self) -> None:
        """Remove the page icon."""
        await self._object.remove_icon()

    async def set_cover(self, url: str) -> None:
        """Set the page cover to an external image URL.

        Args:
            url: Public URL of the cover image.
        """
        await self._object.set_cover_url(url)

    async def random_cover(self) -> None:
        """Set the page cover to a random Notion gradient."""
        await self._object.set_random_cover()

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        """Upload a local file and set it as the page cover.

        Args:
            file_path: Path to the image file.
        """
        await self._object.set_cover_from_file(file_path)

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        """Upload raw bytes and set them as the page cover.

        Args:
            content: Raw image bytes.
            filename: Filename with extension for MIME detection.
        """
        await self._object.set_cover_from_bytes(content, filename)

    async def remove_cover(self) -> None:
        """Remove the page cover image."""
        await self._object.remove_cover()

    async def append(self, content: str) -> None:
        """Append markdown content to the end of the page.

        Args:
            content: Markdown string to append.
        """
        await self._content.append(content=content)

    async def replace(self, content: str) -> None:
        """Replace the entire page body with new markdown content.

        Args:
            content: Markdown string that replaces existing content.
        """
        await self._content.replace(content=content)

    async def clear(self) -> None:
        """Remove all content from the page."""
        await self._content.clear()

    async def get_markdown(self) -> str:
        """Return the full page content as a markdown string."""
        return await self._content.get_markdown()

    async def comment(self, text: str) -> None:
        """Add a top-level comment to the page.

        Args:
            text: Markdown text of the comment.
        """
        await self._comments.create(text)

    async def rename(self, title: str) -> None:
        """Rename the page.

        Args:
            title: New page title.
        """
        await self.properties.set_title(title)
        self.title = title

    async def lock(self) -> None:
        """Lock the page to prevent editing."""
        await self._patch(PageUpdateRequest(is_locked=True))

    async def unlock(self) -> None:
        """Unlock the page to allow editing."""
        await self._patch(PageUpdateRequest(is_locked=False))

    async def erase_content(self) -> None:
        """Permanently erase all page content."""
        await self._patch(PageUpdateRequest(erase_content=True))

    async def apply_default_template(
        self,
        timezone: str | None = None,
        erase_content: bool = False,
    ) -> None:
        """Apply the database's default template to this page.

        Args:
            timezone: IANA timezone for date properties (e.g. ``"Europe/Berlin"``).
            erase_content: If ``True``, remove existing content before applying.
        """
        template = _DefaultTemplate(timezone=timezone)
        await self._patch(
            PageUpdateRequest(
                template=template,
                erase_content=erase_content or None,
            )
        )

    async def apply_template(
        self,
        template_id: UUID,
        timezone: str | None = None,
        erase_content: bool = False,
    ) -> None:
        """Apply a specific template to this page.

        Args:
            template_id: UUID of the template to apply.
            timezone: IANA timezone for date properties.
            erase_content: If ``True``, remove existing content before applying.
        """
        template = _TemplateById(template_id=template_id, timezone=timezone)
        await self._patch(
            PageUpdateRequest(
                template=template,
                erase_content=erase_content or None,
            )
        )

    async def _patch(self, request: PageUpdateRequest) -> None:
        await self._http.patch(self._path, data=request)

    async def update(
        self,
        *,
        title: str | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        cover_url: str | None = None,
        content: str | None = None,
        append_content: str | None = None,
        properties: dict[str, AnyPageProperty] | None = None,
    ) -> None:
        """Update multiple page attributes in a single agent-friendly call.

        All parameters are optional — only provided values are applied.

        Args:
            title: New page title.
            icon_emoji: Emoji to set as the page icon.
            icon_url: External URL to set as the page icon.
            cover_url: External URL to set as the page cover.
            content: Markdown that replaces the entire page body.
            append_content: Markdown to append to the existing page body.
            properties: Property key/value pairs to update.
        """
        if title is not None:
            await self.rename(title)
        await self._object.update(
            icon_emoji=icon_emoji,
            icon_url=icon_url,
            cover_url=cover_url,
        )
        if properties is not None:
            await self.properties.update(properties)
        if content is not None:
            await self.replace(content)
        elif append_content is not None:
            await self.append(append_content)

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"

    def __repr__(self) -> str:
        return f"Page(id={self.id!r}, title={self.title!r})"
