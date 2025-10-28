import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Self, cast

from notionary.file_upload.service import NotionFileUpload
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.file import ExternalFile, FileType, NotionHostedFile
from notionary.shared.models.icon import EmojiIcon, IconType
from notionary.shared.models.parent import ParentType
from notionary.user.base import BaseUser
from notionary.user.service import UserService
from notionary.utils.mixins.logging import LoggingMixin
from notionary.utils.uuid_utils import extract_uuid


class Entity(LoggingMixin, ABC):
    def __init__(
        self,
        dto: EntityResponseDto,
        user_service: UserService | None = None,
        file_upload_service: NotionFileUpload | None = None,
    ) -> None:
        self._id = dto.id
        self._created_time = dto.created_time
        self._created_by = dto.created_by
        self._last_edited_time = dto.last_edited_time
        self._last_edited_by = dto.last_edited_by
        self._in_trash = dto.in_trash
        self._parent = dto.parent
        self._url = dto.url
        self._public_url = dto.public_url

        self._emoji_icon = self._extract_emoji_icon(dto)
        self._external_icon_url = self._extract_external_icon_url(dto)
        self._cover_image_url = self._extract_cover_image_url(dto)

        self._user_service = user_service or UserService()
        self._file_upload_service = file_upload_service or NotionFileUpload()

    @staticmethod
    def _extract_emoji_icon(dto: EntityResponseDto) -> str | None:
        if dto.icon is None:
            return None
        if dto.icon.type is not IconType.EMOJI:
            return None

        emoji_icon = cast(EmojiIcon, dto.icon)
        return emoji_icon.emoji

    @staticmethod
    def _extract_external_icon_url(dto: EntityResponseDto) -> str | None:
        if dto.icon is None:
            return None

        if dto.icon.type == IconType.EXTERNAL:
            external_icon = cast(ExternalFile, dto.icon)
            return external_icon.external.url
        elif dto.icon.type == IconType.FILE:
            notion_file_icon = cast(NotionHostedFile, dto.icon)
            return notion_file_icon.file.url

        return None

    @staticmethod
    def _extract_cover_image_url(dto: EntityResponseDto) -> str | None:
        if dto.cover is None:
            return None

        if dto.cover.type == FileType.EXTERNAL:
            external_cover = cast(ExternalFile, dto.cover)
            return external_cover.external.url
        elif dto.cover.type == FileType.FILE:
            notion_file_cover = cast(NotionHostedFile, dto.cover)
            return notion_file_cover.file.url

        return None

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
        entity_id = extract_uuid(url)
        if not entity_id:
            raise ValueError(f"Could not extract entity ID from URL: {url}")
        return await cls.from_id(entity_id)

    @property
    @abstractmethod
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient: ...

    @property
    def id(self) -> str:
        return self._id

    @property
    def created_time(self) -> str:
        return self._created_time

    @property
    def last_edited_time(self) -> str:
        return self._last_edited_time

    @property
    def in_trash(self) -> bool:
        return self._in_trash

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
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    def get_parent_database_id_if_present(self) -> str | None:
        if self._parent.type == ParentType.DATABASE_ID:
            return self._parent.database_id
        return None

    def get_parent_data_source_id_if_present(self) -> str | None:
        if self._parent.type == ParentType.DATA_SOURCE_ID:
            return self._parent.data_source_id
        return None

    def get_parent_page_id_if_present(self) -> str | None:
        if self._parent.type == ParentType.PAGE_ID:
            return self._parent.page_id
        return None

    def get_parent_block_id_if_present(self) -> str | None:
        if self._parent.type == ParentType.BLOCK_ID:
            return self._parent.block_id
        return None

    def is_workspace_parent(self) -> bool:
        return self._parent.type == ParentType.WORKSPACE

    async def get_created_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._created_by.id)

    async def get_last_edited_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._last_edited_by.id)

    async def set_emoji_icon(self, emoji: str) -> None:
        entity_response = await self._entity_metadata_update_client.patch_emoji_icon(
            emoji
        )
        self._emoji_icon = self._extract_emoji_icon(entity_response)
        self._external_icon_url = None

    async def set_external_icon(self, icon_url: str) -> None:
        entity_response = await self._entity_metadata_update_client.patch_external_icon(
            icon_url
        )
        self._emoji_icon = None
        self._external_icon_url = self._extract_external_icon_url(entity_response)

    async def set_icon_from_file(
        self, file_path: Path, filename: str | None = None
    ) -> None:
        upload_response = await self._file_upload_service.upload_file(
            file_path, filename
        )
        await self.set_icon_from_file_upload(upload_response.id)

    async def set_icon_from_bytes(
        self, file_content: bytes, filename: str, content_type: str | None = None
    ) -> None:
        upload_response = await self._file_upload_service.upload_from_bytes(
            file_content, filename, content_type
        )
        await self.set_icon_from_file_upload(upload_response.id)

    async def set_icon_from_file_upload(self, file_upload_id: str) -> None:
        entity_response = (
            await self._entity_metadata_update_client.patch_icon_from_file_upload(
                file_upload_id
            )
        )
        self._emoji_icon = None
        self._external_icon_url = self._extract_external_icon_url(entity_response)

    async def remove_icon(self) -> None:
        await self._entity_metadata_update_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None

    async def set_cover_image_by_url(self, image_url: str) -> None:
        entity_response = (
            await self._entity_metadata_update_client.patch_external_cover(image_url)
        )
        self._cover_image_url = self._extract_cover_image_url(entity_response)

    async def set_cover_image_from_file(
        self, file_path: Path, filename: str | None = None
    ) -> None:
        upload_response = await self._file_upload_service.upload_file(
            file_path, filename
        )
        await self.set_cover_image_from_file_upload(upload_response.id)

    async def set_cover_image_from_bytes(
        self, file_content: bytes, filename: str, content_type: str | None = None
    ) -> None:
        upload_response = await self._file_upload_service.upload_from_bytes(
            file_content, filename, content_type
        )
        await self.set_cover_image_from_file_upload(upload_response.id)

    async def set_cover_image_from_file_upload(self, file_upload_id: str) -> None:
        entity_response = (
            await self._entity_metadata_update_client.patch_cover_from_file_upload(
                file_upload_id
            )
        )
        self._cover_image_url = self._extract_cover_image_url(entity_response)

    async def set_random_gradient_cover(self) -> None:
        random_cover_url = self._get_random_gradient_cover()
        await self.set_cover_image_by_url(random_cover_url)

    async def remove_cover_image(self) -> None:
        await self._entity_metadata_update_client.remove_cover()
        self._cover_image_url = None

    async def move_to_trash(self) -> None:
        if self._in_trash:
            self.logger.warning("Entity is already in trash.")
            return

        entity_response = await self._entity_metadata_update_client.move_to_trash()
        self._in_trash = entity_response.in_trash

    async def restore_from_trash(self) -> None:
        if not self._in_trash:
            self.logger.warning("Entity is not in trash.")
            return

        entity_response = await self._entity_metadata_update_client.restore_from_trash()
        self._in_trash = entity_response.in_trash

    def __repr__(self) -> str:
        attrs = []
        for key, value in self.__dict__.items():
            if key.startswith("_") and not key.startswith("__"):
                attr_name = key[1:]
                attrs.append(f"{attr_name}={value!r}")

        attrs_str = ", ".join(attrs)
        return f"{self.__class__.__name__}({attrs_str})"

    def _get_random_gradient_cover(self) -> str:
        DEFAULT_NOTION_COVERS: Sequence[str] = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 10)
        ]

        return random.choice(DEFAULT_NOTION_COVERS)
