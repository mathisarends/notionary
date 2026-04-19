import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import overload
from uuid import UUID

from notionary.data_source.client import (
    DataSourceClient,
)
from notionary.data_source.properties.properties import (
    DataSourceProperties,
)
from notionary.data_source.properties.schemas import (
    AnyDataSourceProperty,
)
from notionary.data_source.properties.views import (
    DataSourcePropertyDescription,
    DataSourceRelationOption,
)
from notionary.data_source.query.filters import QueryFilter
from notionary.data_source.query.sorts import QuerySort
from notionary.data_source.schemas import DataSourceTemplate
from notionary.file_upload import FileUploads
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.rich_text import rich_text_to_markdown
from notionary.shared.object import NotionObject
from notionary.shared.object.icon.schemas import Icon
from notionary.shared.object.schemas import File
from notionary.user.schemas import PartialUserDto

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
        icon: Icon | None,
        cover: File | None,
        in_trash: bool,
        properties: dict[str, AnyDataSourceProperty],
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
        self.created_time = created_time
        self.created_by = created_by
        self.last_edited_time = last_edited_time
        self.last_edited_by = last_edited_by
        self._http = http

        path = f"data_sources/{id}"
        file_uploads = FileUploads(http)
        self._object = NotionObject(
            icon=icon,
            cover=cover,
            in_trash=in_trash,
            http_client=http,
            path=path,
            file_uploads=file_uploads,
        )

        self.properties = properties or {}
        self._properties = DataSourceProperties(properties=self.properties)
        self._client = DataSourceClient(http=http, data_source_id=id)

    @property
    def in_trash(self) -> bool:
        """Whether this data source is in the trash."""
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
        """Move the data source to the trash."""
        await self._object.trash()

    async def restore(self) -> None:
        """Restore the data source from the trash."""
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
        """Set the data source icon from an emoji, URL, local file, or raw bytes.

        A string starting with ``http`` is treated as an external URL;
        any other string is treated as an emoji character.

        Args:
            source: An emoji, a public image URL, a local file path, or raw bytes.
            filename: Required when *source* is bytes — used for MIME detection.
        """
        await self._object.set_icon(source, filename)

    async def remove_icon(self) -> None:
        """Remove the data source icon."""
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
        """Set the data source cover from a URL, local file, or raw bytes.

        Args:
            source: A public image URL, a local file path, or raw image bytes.
            filename: Required when *source* is bytes — used for MIME detection.
        """
        await self._object.set_cover(source, filename)

    async def random_cover(self) -> None:
        """Set the data source cover to a random Notion gradient."""
        await self._object.set_random_cover()

    async def remove_cover(self) -> None:
        """Remove the data source cover image."""
        await self._object.remove_cover()

    async def set_title(self, title: str) -> None:
        """Update the data source title.

        Args:
            title: New title.
        """
        dto = await self._client.set_title(title)
        title_markdown = rich_text_to_markdown(dto.title)
        self.title = title_markdown

    async def create_page(
        self,
        title: str | None = None,
        *,
        template_id: str | None = None,
        use_default_template: bool = False,
    ) -> Page:
        """Create a new page inside this data source.

        Args:
            title: Optional page title.
            template_id: ID of the template to apply. Takes precedence over
                *use_default_template* when both are supplied.
            use_default_template: If ``True`` and no *template_id* is given,
                apply the data source's default template.

        Returns:
            The newly created :class:`~notionary.page.page.Page`.
        """
        return await self._client.create_page(
            title=title,
            template_id=template_id,
            use_default_template=use_default_template,
        )

    async def list_templates(
        self,
        name: str | None = None,
        page_size: int = 100,
    ) -> list[DataSourceTemplate]:
        """List all page templates available in this data source.

        Args:
            name: Optional case-insensitive substring filter on template name.
            page_size: Number of results per API request (max 100).

        Returns:
            A list of :class:`~notionary.data_source.schemas.DataSourceTemplate` objects.
        """
        return await self._client.list_templates(name=name, page_size=page_size)

    async def query(
        self,
        *,
        filter: QueryFilter | None = None,
        sorts: list[QuerySort] | None = None,
        page_size: int | None = None,
        filter_properties: list[str] | None = None,
        in_trash: bool | None = None,
        limit: int | None = None,
    ) -> list[Page]:
        """Query pages in this data source with optional filters and sorts.

        Args:
            filter: A property, timestamp, or compound filter.
            sorts: Ordering criteria (property or timestamp sorts).
            page_size: Number of results per API request (max 100).
            filter_properties: Property names/IDs to include in results.
            in_trash: If ``True``, return only trashed pages.
            limit: Maximum total number of pages to return.

        Returns:
            A list of :class:`~notionary.page.page.Page` objects.
        """
        return await self._client.query(
            filter=filter,
            sorts=sorts,
            page_size=page_size,
            filter_properties=filter_properties,
            in_trash=in_trash,
            limit=limit,
        )

    async def iter_query(
        self,
        *,
        filter: QueryFilter | None = None,
        sorts: list[QuerySort] | None = None,
        page_size: int | None = None,
        filter_properties: list[str] | None = None,
        in_trash: bool | None = None,
        limit: int | None = None,
    ) -> AsyncGenerator[Page]:
        """Stream pages from this data source with optional filters and sorts.

        Yields pages one by one without loading the full result set into memory.

        Args:
            filter: A property, timestamp, or compound filter.
            sorts: Ordering criteria (property or timestamp sorts).
            page_size: Number of results per API request (max 100).
            filter_properties: Property names/IDs to include in results.
            in_trash: If ``True``, return only trashed pages.
            limit: Maximum total number of pages to return.

        Yields:
            :class:`~notionary.page.page.Page` objects one at a time.
        """
        async for page in self._client.iter_query(
            filter=filter,
            sorts=sorts,
            page_size=page_size,
            filter_properties=filter_properties,
            in_trash=in_trash,
            limit=limit,
        ):
            yield page

    async def update(
        self,
        *,
        title: str | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        cover_url: str | None = None,
    ) -> None:
        """Update multiple data source attributes in a single agent-friendly call.

        All parameters are optional — only provided values are applied.

        Args:
            title: New data source title.
            icon_emoji: Emoji to set as the data source icon.
            icon_url: External URL to set as the data source icon.
            cover_url: External URL to set as the data source cover.
        """
        if title is not None:
            await self.set_title(title)
        await self._object.update(
            icon_emoji=icon_emoji,
            icon_url=icon_url,
            cover_url=cover_url,
        )

    def describe_properties(self) -> dict[str, DataSourcePropertyDescription]:
        """Return a structured schema description of all data source properties.

        Designed for LLM context injection — each entry is a typed
        :class:`~notionary.data_source.properties.views.DataSourcePropertyDescription`.
        """
        return self._properties.describe()

    async def describe_properties_with_relation_pages(
        self,
        *,
        page_size: int = 100,
        limit: int | None = 100,
    ) -> dict[str, DataSourcePropertyDescription]:
        """Describe properties and resolve relation options to related pages.

        For relation properties, this method queries the related data source and
        returns page-level options as ``title + id`` pairs.

        Args:
            page_size: Number of pages per API request when resolving relation options.
            limit: Maximum total pages to include per relation.
        """
        return await self._properties.describe_with_relation_options(
            lambda relation_data_source_id: self._fetch_relation_page_options(
                relation_data_source_id,
                page_size=page_size,
                limit=limit,
            )
        )

    async def _fetch_relation_page_options(
        self,
        relation_data_source_id: str,
        *,
        page_size: int,
        limit: int | None,
    ) -> list[DataSourceRelationOption]:
        """Fetch relation options as pages from a related data source."""
        try:
            related_id = UUID(relation_data_source_id)
        except ValueError:
            return []

        relation_client = DataSourceClient(http=self._http, data_source_id=related_id)
        pages = await relation_client.query(page_size=page_size, limit=limit)
        return [
            DataSourceRelationOption(id=str(page.id), title=page.title)
            for page in pages
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"

    def __repr__(self) -> str:
        return f"DataSource(id={self.id!r}, title={self.title!r})"
