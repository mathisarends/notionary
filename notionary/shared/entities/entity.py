import re
from abc import ABC, abstractmethod
from typing import Self

from notionary.shared.entities.entity_metadata_client import EntityMetadataClient
from notionary.util import LoggingMixin


class NotionEntity(LoggingMixin, ABC):
    def __init__(
        self,
        id: str,
        title: str,
        url: str,
        archived: bool,
        in_trash: bool,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
    ):
        self._id = id
        self._title = title
        self._url = url
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url

        self._is_archieved = archived
        self._is_in_trash = in_trash

    @classmethod
    @abstractmethod
    async def from_id(cls, id: str) -> Self:
        pass

    @classmethod
    @abstractmethod
    async def from_title(cls, title: str) -> Self:
        pass

    @classmethod
    async def from_url(cls, url: str) -> Self:
        entity_id = cls._extract_uuid(url)
        if not entity_id:
            raise ValueError(f"Could not extract entity ID from URL: {url}")
        return await cls.from_id(entity_id)

    @property
    @abstractmethod
    def _metadata_client(self) -> EntityMetadataClient:
        """Return the concrete metadata client for this entity."""
        ...

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def external_icon_url(self) -> str | None:
        return self._external_icon_url

    @property
    def emoji_icon(self) -> str | None:
        return self._emoji_icon

    @property
    def cover_image_url(self) -> str | None:
        return self._cover_image_url

    @property
    def is_archived(self) -> bool:
        return self._is_archieved

    @property
    def is_in_trash(self) -> bool:
        return self._is_in_trash

    async def set_title(self, title: str) -> None:
        await self._metadata_client.set_title(title)
        self._title = title

    async def set_emoji_icon(self, emoji: str) -> None:
        entity_response = await self._metadata_client.patch_emoji_icon(emoji)
        self._emoji_icon = entity_response.icon.emoji
        self._external_icon_url = None

    async def set_external_icon(self, icon_url: str) -> None:
        entity_response = await self._metadata_client.patch_external_icon(icon_url)
        self._emoji_icon = None
        self._external_icon_url = entity_response.icon.external.url

    async def remove_icon(self) -> None:
        await self._metadata_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None

    async def set_cover_image_by_url(self, image_url: str) -> None:
        entity_response = await self._metadata_client.patch_external_cover(image_url)
        self._cover_image_url = entity_response.cover.external.url

    async def set_random_gradient_cover(self) -> None:
        random_cover_url = self._get_random_gradient_cover()
        await self.set_cover_image_by_url(random_cover_url)

    async def remove_cover_image(self) -> None:
        await self._metadata_client.remove_cover()
        self._cover_image_url = None

    async def archive(self) -> None:
        if self._is_archieved:
            self.logger.info("Entity is already archived.")
            return

        entity_response = await self._metadata_client.archive_page()
        self._is_archieved = entity_response.archived

    async def unarchive(self) -> None:
        if not self._is_archieved:
            self.logger.info("Entity is not archived.")
            return

        entity_response = await self._metadata_client.unarchive_page()
        self._is_archieved = entity_response.archived

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"title={self._title!r}, "
            f"url={self._url!r}, "
            f"archived={self._is_archieved!r}, "
            f"in_trash={self._is_in_trash!r}, "
            f"emoji_icon={self._emoji_icon!r}, "
            f"external_icon_url={self._external_icon_url!r}, "
            f"cover_image_url={self._cover_image_url!r}"
            f")"
        )

    def _get_random_gradient_cover(self) -> str:
        import random
        from collections.abc import Sequence

        DEFAULT_NOTION_COVERS: Sequence[str] = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png" for i in range(1, 10)
        ]

        return random.choice(DEFAULT_NOTION_COVERS)

    @staticmethod
    def _extract_uuid(source: str) -> str | None:
        UUID_RAW_PATTERN = r"([a-f0-9]{32})"

        if NotionEntity._is_valid_uuid(source):
            return source

        match = re.search(UUID_RAW_PATTERN, source.lower())
        if not match:
            return None

        uuid_raw = match.group(1)
        return f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"

    @staticmethod
    def _is_valid_uuid(uuid: str) -> bool:
        UUID_PATTERN = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
        return bool(re.match(UUID_PATTERN, uuid.lower()))
