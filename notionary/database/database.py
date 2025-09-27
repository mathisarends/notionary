from __future__ import annotations

from notionary.database.database_factory import (
    load_database_from_id,
    load_database_from_title,
)
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.page.page import NotionPage
from notionary.page.page_models import NotionPageDto
from notionary.util import LoggingMixin


class NotionDatabase(LoggingMixin):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
        url: str,
        in_trash: bool,
        is_inline: bool,
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
    ) -> None:
        self._id = id
        self._title = title
        self._created_time = created_time
        self._last_edited_time = last_edited_time
        self._url = url
        self._public_url = public_url
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url
        self._in_trash = in_trash
        self._description = description
        self._is_inline = is_inline

        self.client = NotionDatabseHttpClient(database_id=id)

        self._metadata_update_client = DatabaseMetadataUpdateClient(database_id=id)
        """ self.property_reader = DatabasePropertyReader(self) """

    @classmethod
    async def from_id(cls, id: str) -> NotionDatabase:
        return await load_database_from_id(id)

    @classmethod
    async def from_title(
        cls,
        title: str,
        min_similarity: float = 0.6,
    ) -> NotionDatabase:
        return await load_database_from_title(title, min_similarity)

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def created_time(self) -> str:
        return self._created_time

    @property
    def last_edited_time(self) -> str:
        return self._last_edited_time

    @property
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    @property
    def emoji_icon(self) -> str | None:
        return self._emoji_icon

    @property
    def external_icon_url(self) -> str | None:
        return self._external_icon_url

    @property
    def cover_image_url(self) -> str | None:
        return self._cover_image_url

    @property
    def in_trash(self) -> bool:
        return self._in_trash

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def is_inline(self) -> bool:
        return self._is_inline

    async def create_blank_page(self) -> NotionPage:
        create_page_response: NotionPageDto = await self.client.create_page()

        return await NotionPage.from_id(create_page_response.id)

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text

    async def set_description(self, description: str) -> None:
        updated_description = await self.client.update_database_description(description=description)
        self._description = updated_description

    async def set_emoji_icon(self, emoji: str) -> None:
        entity_response = await self._metadata_update_client.patch_emoji_icon(emoji)
        self._emoji_icon = entity_response.icon.emoji if entity_response.icon else None
        self._external_icon_url = None

    async def set_external_icon(self, icon_url: str) -> None:
        entity_response = await self._metadata_update_client.patch_external_icon(icon_url)
        self._emoji_icon = None
        self._external_icon_url = (
            entity_response.icon.external.url if entity_response.icon and entity_response.icon.external else None
        )

    async def remove_icon(self) -> None:
        await self._metadata_update_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None

    async def set_cover_image_by_url(self, image_url: str) -> None:
        entity_response = await self._metadata_update_client.patch_external_cover(image_url)
        self._cover_image_url = (
            entity_response.cover.external.url if entity_response.cover and entity_response.cover.external else None
        )

    async def remove_cover_image(self) -> None:
        await self._metadata_update_client.remove_cover()
        self._cover_image_url = None

    def filter(self) -> DatabaseFilterBuilder:
        return DatabaseFilterBuilder(database=self)

    async def find_by_title(self, title: str) -> list[NotionPage]:
        return await self.filter().title_contains(title).to_list()

    async def all_pages(self, page_size: int = 100) -> list[NotionPage]:
        return await self.filter().page_size(page_size).to_list()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"title={self._title!r}, "
            f"created_time={self._created_time!r}, "
            f"last_edited_time={self._last_edited_time!r}, "
            f"url={self._url!r}, "
            f"public_url={self._public_url!r}, "
            f"in_trash={self._in_trash!r}, "
            f"is_inline={self._is_inline!r}, "
            f"emoji_icon={self._emoji_icon!r}, "
            f"external_icon_url={self._external_icon_url!r}, "
            f"cover_image_url={self._cover_image_url!r}, "
            f"description={self._description!r}"
            f")"
        )
