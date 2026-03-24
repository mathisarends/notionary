import logging

from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import EntityResponseDto

logger = logging.getLogger(__name__)


class EntityTrash:
    def __init__(
        self,
        dto: EntityResponseDto,
        update_client: EntityMetadataUpdateClient,
    ) -> None:
        self._client = update_client
        self._in_trash = dto.in_trash

    @property
    def in_trash(self) -> bool:
        return self._in_trash

    async def move_to_trash(self) -> None:
        if self._in_trash:
            logger.warning("Entity is already in trash.")
            return
        response = await self._client.move_to_trash()
        self._in_trash = response.in_trash

    async def restore(self) -> None:
        if not self._in_trash:
            logger.warning("Entity is not in trash.")
            return
        response = await self._client.restore_from_trash()
        self._in_trash = response.in_trash
