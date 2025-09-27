from abc import ABC, abstractmethod

from notionary.shared.entity.entity import Entity
from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType


class EntityFactory[T: Entity](ABC):
    @abstractmethod
    async def load_from_id(self, entity_id: str) -> T:
        pass

    @abstractmethod
    async def load_from_title(self, title: str, min_similarity: float = 0.6) -> T:
        pass

    def _create_common_entity_kwargs(self, response: EntityDto) -> dict:
        emoji_icon = self._extract_emoji_icon(response)
        external_icon_url = self._extract_external_icon_url(response)
        cover_image_url = self._extract_cover_image_url(response)

        return {
            "id": response.id,
            "created_time": response.created_time,
            "last_edited_time": response.last_edited_time,
            "in_trash": response.in_trash,
            "emoji_icon": emoji_icon,
            "external_icon_url": external_icon_url,
            "cover_image_url": cover_image_url,
        }

    def _extract_emoji_icon(self, response: EntityDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EMOJI:
            return None
        return response.icon.emoji

    def _extract_external_icon_url(self, response: EntityDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EXTERNAL:
            return None
        return response.icon.external.url if response.icon.external else None

    def _extract_cover_image_url(self, response: EntityDto) -> str | None:
        if not response.cover or response.cover.type != CoverType.EXTERNAL:
            return None
        return response.cover.external.url if response.cover.external else None
