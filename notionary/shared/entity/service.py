from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Self

from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.models.parent import Parent, ParentType
from notionary.user.schemas import PartialUserDto
from notionary.user.service import UserService
from notionary.utils.mixins.logging import LoggingMixin
from notionary.utils.uuid_utils import extract_uuid

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionDataSource, NotionPage
    from notionary.user.base import BaseUser


class Entity(LoggingMixin, ABC):
    def __init__(
        self,
        id: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        in_trash: bool,
        parent: Parent,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        user_service: UserService | None = None,
    ) -> None:
        self._id = id
        self._created_time = created_time
        self._created_by = created_by
        self._last_edited_time = last_edited_time
        self._last_edited_by = last_edited_by
        self._in_trash = in_trash
        self._parent = parent
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url
        self._user_service = user_service or UserService()

        # Lazy-loaded parent entities cache
        self._cached_parent_database: NotionDatabase | None = None
        self._cached_parent_data_source: NotionDataSource | None = None
        self._cached_parent_page: NotionPage | None = None

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
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        # functionality for updating properties like title, icon, cover, archive status depends on interface for template like implementation
        # has to be implementated by inheritants to correctly use the methods below
        ...

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
    def created_by(self) -> PartialUserDto:
        return self._created_by

    # =========================================================================
    # Parent ID Getters
    # =========================================================================

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

    # =========================================================================
    # User Methods
    # =========================================================================

    async def get_created_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._created_by.id)

    async def get_last_edited_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._last_edited_by.id)

    # =========================================================================
    # Icon & Cover Methods
    # =========================================================================

    async def set_emoji_icon(self, emoji: str) -> None:
        entity_response = await self._entity_metadata_update_client.patch_emoji_icon(emoji)
        self._emoji_icon = entity_response.icon.emoji if entity_response.icon else None
        self._external_icon_url = None

    async def set_external_icon(self, icon_url: str) -> None:
        entity_response = await self._entity_metadata_update_client.patch_external_icon(icon_url)
        self._emoji_icon = None
        self._external_icon_url = (
            entity_response.icon.external.url if entity_response.icon and entity_response.icon.external else None
        )

    async def remove_icon(self) -> None:
        await self._entity_metadata_update_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None

    async def set_cover_image_by_url(self, image_url: str) -> None:
        entity_response = await self._entity_metadata_update_client.patch_external_cover(image_url)
        self._cover_image_url = (
            entity_response.cover.external.url if entity_response.cover and entity_response.cover.external else None
        )

    async def set_random_gradient_cover(self) -> None:
        random_cover_url = self._get_random_gradient_cover()
        await self.set_cover_image_by_url(random_cover_url)

    async def remove_cover_image(self) -> None:
        await self._entity_metadata_update_client.remove_cover()
        self._cover_image_url = None

    # =========================================================================
    # Trash Methods
    # =========================================================================

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
            f"https://www.notion.so/images/page-cover/gradients_{i}.png" for i in range(1, 10)
        ]

        return random.choice(DEFAULT_NOTION_COVERS)
