import logging
import random
import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Self, cast

from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.icon import EmojiIcon, IconType
from notionary.shared.models.parent import ParentType

logger = logging.getLogger(__name__)

_UUID_RAW_PATTERN = re.compile(r"([a-f0-9]{32})")
_UUID_PATTERN = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
)

_DEFAULT_NOTION_COVERS: Sequence[str] = [
    f"https://www.notion.so/images/page-cover/gradients_{i}.png" for i in range(1, 10)
]


def _is_valid_uuid(uuid: str) -> bool:
    return bool(_UUID_PATTERN.match(uuid.lower()))


def _extract_uuid(source: str) -> str | None:
    if _is_valid_uuid(source):
        return source
    match = _UUID_RAW_PATTERN.search(source.lower())
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


class Entity(ABC):
    def __init__(
        self,
        dto: EntityResponseDto,
        # user_service: UserService | None = None,
        # file_upload_service: NotionFileUpload | None = None,
    ) -> None:
        self.id = dto.id
        self.created_time = dto.created_time
        self.created_by = dto.created_by
        self.last_edited_time = dto.last_edited_time
        self.last_edited_by = dto.last_edited_by
        self.in_trash = dto.in_trash
        self.parent = dto.parent
        self.url = dto.url
        self.public_url = dto.public_url

        self.emoji_icon = self._extract_emoji_icon(dto)
        self.icon_url = self._extract_icon_url(dto)
        self.cover_url = self._extract_cover_url(dto)

        # self._user_service = user_service or UserService()
        # self._file_upload_service = file_upload_service or NotionFileUpload()

    @staticmethod
    def _extract_emoji_icon(dto: EntityResponseDto) -> str | None:
        if dto.icon is None or dto.icon.type is not IconType.EMOJI:
            return None
        return cast(EmojiIcon, dto.icon).emoji

    @staticmethod
    def _extract_icon_url(dto: EntityResponseDto) -> str | None:
        return dto.icon.get_url() if dto.icon else None

    @staticmethod
    def _extract_cover_url(dto: EntityResponseDto) -> str | None:
        return dto.cover.get_url() if dto.cover else None

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
        entity_id = _extract_uuid(url)
        if not entity_id:
            raise ValueError(f"Could not extract entity ID from URL: {url}")
        return await cls.from_id(entity_id)

    @property
    @abstractmethod
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient: ...

    def parent_database_id(self) -> str | None:
        if self.parent.type == ParentType.DATABASE_ID:
            return self.parent.database_id
        return None

    def parent_data_source_id(self) -> str | None:
        if self.parent.type == ParentType.DATA_SOURCE_ID:
            return self.parent.data_source_id
        return None

    def parent_page_id(self) -> str | None:
        if self.parent.type == ParentType.PAGE_ID:
            return self.parent.page_id
        return None

    def parent_block_id(self) -> str | None:
        if self.parent.type == ParentType.BLOCK_ID:
            return self.parent.block_id
        return None

    def is_workspace_parent(self) -> bool:
        return self.parent.type == ParentType.WORKSPACE

    async def set_emoji(self, emoji: str) -> None:
        response = await self._entity_metadata_update_client.patch_emoji_icon(emoji)
        self.emoji_icon = self._extract_emoji_icon(response)
        self.icon_url = None

    async def set_icon(self, icon_url: str) -> None:
        response = await self._entity_metadata_update_client.patch_external_icon(
            icon_url
        )
        self.emoji_icon = None
        self.icon_url = self._extract_icon_url(response)

    async def set_icon_file(self, file_path: Path, filename: str | None = None) -> None:
        upload = await self._file_upload_service.upload_file(file_path, filename)
        await self.set_icon_upload(upload.id)

    async def set_icon_bytes(
        self, file_content: bytes, filename: str, content_type: str | None = None
    ) -> None:
        upload = await self._file_upload_service.upload_from_bytes(
            file_content, filename, content_type
        )
        await self.set_icon_upload(upload.id)

    async def set_icon_upload(self, file_upload_id: str) -> None:
        response = (
            await self._entity_metadata_update_client.patch_icon_from_file_upload(
                file_upload_id
            )
        )
        self.emoji_icon = None
        self.icon_url = self._extract_icon_url(response)

    async def remove_icon(self) -> None:
        await self._entity_metadata_update_client.remove_icon()
        self.emoji_icon = None
        self.icon_url = None

    async def set_cover(self, image_url: str) -> None:
        response = await self._entity_metadata_update_client.patch_external_cover(
            image_url
        )
        self.cover_url = self._extract_cover_url(response)

    async def set_cover_file(
        self, file_path: Path, filename: str | None = None
    ) -> None:
        upload = await self._file_upload_service.upload_file(file_path, filename)
        await self.set_cover_upload(upload.id)

    async def set_cover_bytes(
        self, file_content: bytes, filename: str, content_type: str | None = None
    ) -> None:
        upload = await self._file_upload_service.upload_from_bytes(
            file_content, filename, content_type
        )
        await self.set_cover_upload(upload.id)

    async def set_cover_upload(self, file_upload_id: str) -> None:
        response = (
            await self._entity_metadata_update_client.patch_cover_from_file_upload(
                file_upload_id
            )
        )
        self.cover_url = self._extract_cover_url(response)

    async def random_cover(self) -> None:
        await self.set_cover(random.choice(_DEFAULT_NOTION_COVERS))

    async def remove_cover(self) -> None:
        await self._entity_metadata_update_client.remove_cover()
        self.cover_url = None

    async def trash(self) -> None:
        if self.in_trash:
            logger.warning("Entity is already in trash.")
            return
        response = await self._entity_metadata_update_client.move_to_trash()
        self.in_trash = response.in_trash

    async def restore(self) -> None:
        if not self.in_trash:
            logger.warning("Entity is not in trash.")
            return
        response = await self._entity_metadata_update_client.restore_from_trash()
        self.in_trash = response.in_trash

    def __repr__(self) -> str:
        attrs = [
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        ]
        return f"{self.__class__.__name__}({', '.join(attrs)})"
