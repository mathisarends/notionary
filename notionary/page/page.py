from pathlib import Path
from typing import overload
from uuid import UUID

from notionary.file_upload import FileUploads
from notionary.http import HttpClient
from notionary.page.comments.service import PageComments
from notionary.page.content import PageContent
from notionary.page.properties import PageProperties
from notionary.page.properties.schemas import AnyPageProperty
from notionary.page.properties.views import PagePropertyDescription
from notionary.page.schemas import (
    DataSourceParent,
    MovePageRequest,
    PageParent,
    PageUpdateRequest,
    _DefaultTemplate,
    _TemplateById,
)
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
        data_source_id: UUID | None = None,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.created_time = created_time
        self.created_by = created_by
        self.last_edited_time = last_edited_time
        self.last_edited_by = last_edited_by
        self.data_source_id = data_source_id

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

        self.properties = PageProperties(
            id=id,
            properties=properties,
            http=http,
            data_source_id=data_source_id,
        )

        self._content = PageContent(page_id=id, http=http)
        self._comments = PageComments(page_id=id, http=http)

    @property
    def in_trash(self) -> bool:
        """Whether this page is in the trash."""
        return self._object.in_trash

    @property
    def icon_emoji(self) -> str | None:
        """The current icon emoji, or ``None`` if no emoji icon is set."""
        return self._object.icon_emoji

    @property
    def icon_url(self) -> str | None:
        """The current icon URL, or ``None`` if no URL icon is set."""
        return self._object.icon_url

    @property
    def cover_url(self) -> str | None:
        """The current cover URL, or ``None`` if no cover is set."""
        return self._object.cover_url

    async def trash(self) -> None:
        """Move the page to the trash."""
        await self._object.trash()

    async def restore(self) -> None:
        """Restore the page from the trash."""
        await self._object.restore()

    @overload
    async def set_icon(self, source: str) -> None: ...
    @overload
    async def set_icon(self, source: Path) -> None: ...
    @overload
    async def set_icon(self, source: bytes, filename: str) -> None: ...

    async def set_icon(
        self,
        source: str | Path | bytes,
        filename: str | None = None,
    ) -> None:
        """Set the page icon from an emoji, URL, local file, or raw bytes.

        A string starting with ``http`` is treated as an external URL;
        any other string is treated as an emoji character.

        Args:
            source: An emoji, a public image URL, a local file path, or raw bytes.
            filename: Required when *source* is bytes — used for MIME detection.
        """
        await self._object.set_icon(source, filename)

    async def remove_icon(self) -> None:
        """Remove the page icon."""
        await self._object.remove_icon()

    @overload
    async def set_cover(self, source: str) -> None: ...
    @overload
    async def set_cover(self, source: Path) -> None: ...
    @overload
    async def set_cover(self, source: bytes, filename: str) -> None: ...

    async def set_cover(
        self,
        source: str | Path | bytes,
        filename: str | None = None,
    ) -> None:
        """Set the page cover from a URL, local file, or raw bytes.

        Args:
            source: A public image URL, a local file path, or raw image bytes.
            filename: Required when *source* is bytes — used for MIME detection.
        """
        await self._object.set_cover(source, filename)

    async def random_cover(self) -> None:
        """Set the page cover to a random Notion gradient."""
        await self._object.set_random_cover()

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

    async def get_comments(self) -> list:
        """Return all comments on this page.

        Returns:
            A list of :class:`~notionary.page.comments.models.Comment` objects
            with resolved author names.
        """
        return await self._comments.list()

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

    async def set_property(
        self,
        name: str,
        value: str | int | float | bool | list[str] | None,
    ) -> None:
        """Set a page property by its exact property name.

        Args:
            name: Property name as it appears in Notion.
            value: Plain value validated against the property schema.
        """
        await self.properties.set(name, value)

    async def set_properties(self, values: dict[str, object]) -> None:
        """Set multiple page properties in a single API request.

        Args:
            values: Mapping of property names to raw values.
        """
        await self.properties.set_many(values)

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

    async def move_to_page(self, parent_page_id: UUID) -> None:
        """Move this page under another page.

        Args:
            parent_page_id: UUID of the new parent page.
        """
        request = MovePageRequest(parent=PageParent(page_id=parent_page_id))
        await self._http.post(f"{self._path}/move", data=request)

    async def move_to_data_source(self, data_source_id: UUID) -> None:
        """Move this page into a database via its data source.

        Args:
            data_source_id: UUID of the target database's data source.
        """
        request = MovePageRequest(
            parent=DataSourceParent(data_source_id=data_source_id)
        )
        await self._http.post(f"{self._path}/move", data=request)

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
        properties: dict[str, object] | None = None,
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
            await self.set_properties(properties)
        if content is not None:
            await self.replace(content)
        elif append_content is not None:
            await self.append(append_content)

    async def describe_properties(self) -> dict[str, PagePropertyDescription]:
        """Return a structured property schema for this page.

        This is a convenience wrapper around ``self.properties.describe()``
        so agent integrations can call a page-level API directly.
        """
        return await self.properties.describe()

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"

    def __repr__(self) -> str:
        return f"Page(id={self.id!r}, title={self.title!r})"
