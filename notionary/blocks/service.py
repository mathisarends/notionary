from __future__ import annotations

from typing import Self

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.content.factory import BlockContentServiceFactory
from notionary.blocks.content.service import BlockContentService
from notionary.blocks.schemas import Block
from notionary.user.base import BaseUser
from notionary.user.service import UserService
from notionary.utils.mixins.logging import LoggingMixin


class NotionBlock(LoggingMixin):
    def __init__(
        self,
        block: Block,
        block_client: NotionBlockHttpClient,
        block_content_service: BlockContentService,
        user_service: UserService,
    ) -> None:
        self._id = block.id
        self._parent = block.parent
        self._created_time = block.created_time
        self._last_edited_time = block.last_edited_time
        self._created_by_dto = block.created_by
        self._last_edited_by_dto = block.last_edited_by
        self._archived = block.archived
        self._in_trash = block.in_trash
        self._has_children = block.has_children
        self._block_data = block

        self._block_client = block_client
        self._block_content_service = block_content_service
        self._user_service = user_service

    @classmethod
    async def from_id(cls, block_id: str) -> Self:
        block_client = NotionBlockHttpClient()
        block = await block_client.get_block_by_id(block_id)
        return cls._create_with_dependencies(block=block)

    @classmethod
    def from_block(cls, block: Block) -> Self:
        return cls._create_with_dependencies(block=block)

    @classmethod
    def _create_with_dependencies(
        cls,
        block: Block,
    ) -> Self:
        block_client = NotionBlockHttpClient()
        user_service = UserService()

        block_content_service_factory = BlockContentServiceFactory()
        block_content_service = block_content_service_factory.create(
            block_id=block.id, block_client=block_client
        )

        return cls(
            block=block,
            block_client=block_client,
            block_content_service=block_content_service,
            user_service=user_service,
        )

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
    def archived(self) -> bool:
        return self._archived

    @property
    def in_trash(self) -> bool:
        return self._in_trash

    @property
    def has_children(self) -> bool:
        return self._has_children

    async def get_created_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._created_by_dto.id)

    async def get_last_edited_by_user(self) -> BaseUser | None:
        return await self._user_service.get_user_by_id(self._last_edited_by_dto.id)

    async def get_content_as_markdown(self) -> str:
        return await self._block_content_service.get_as_markdown()

    async def get_content_as_blocks(self) -> list[Block]:
        return await self._block_content_service.get_as_blocks()

    async def get_children(self) -> list[NotionBlock]:
        if not self._has_children:
            return []

        blocks = await self._block_client.get_all_block_children(self._id)
        return [self._create_with_dependencies(block=block) for block in blocks]

    async def delete(self) -> None:
        await self._block_client.delete_block(self._id)
