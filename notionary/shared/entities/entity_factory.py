from abc import ABC, abstractmethod
from typing import TypeVar

from notionary.shared.entities.entity_models import NotionEntityResponseDto
from notionary.shared.models.cover_models import CoverType
from notionary.shared.models.icon_models import IconType
from notionary.shared.models.parent_models import ParentType

EntityT = TypeVar("EntityT", bound=object)


class NotionEntityFactory(ABC):
    @abstractmethod
    async def load_from_id(self, entity_id: str) -> EntityT:
        pass

    @abstractmethod
    async def load_from_title(self, title: str, min_similarity: float = 0.6) -> EntityT:
        pass

    @abstractmethod
    async def _extract_title(self, response: NotionEntityResponseDto) -> str:
        pass

    async def _create_common_entity_kwargs(self, response: NotionEntityResponseDto) -> dict:
        title = await self._extract_title(response)
        emoji_icon = self._extract_emoji_icon(response)
        external_icon_url = self._extract_external_icon_url(response)
        cover_image_url = self._extract_cover_image_url(response)

        return {
            "id": response.id,
            "title": title,
            "url": response.url,
            "archived": response.archived,
            "in_trash": response.in_trash,
            "emoji_icon": emoji_icon,
            "external_icon_url": external_icon_url,
            "cover_image_url": cover_image_url,
            "properties": response.properties,
        }

    def _extract_emoji_icon(self, response: NotionEntityResponseDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EMOJI:
            return None
        return response.icon.emoji

    def _extract_external_icon_url(self, response: NotionEntityResponseDto) -> str | None:
        if not response.icon or response.icon.type != IconType.EXTERNAL:
            return None
        return response.icon.external.url if response.icon.external else None

    def _extract_cover_image_url(self, response: NotionEntityResponseDto) -> str | None:
        if not response.cover or response.cover.type != CoverType.EXTERNAL:
            return None
        return response.cover.external.url if response.cover.external else None

    def _extract_parent_database_id(self, response: NotionEntityResponseDto) -> str | None:
        if response.parent.type == ParentType.DATABASE_ID:
            return response.parent.database_id
        return None

    async def _extract_title_from_rich_text_objects(self, rich_text_objects: list) -> str:
        from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter

        rich_text_markdown_converter = RichTextToMarkdownConverter()
        title = await rich_text_markdown_converter.to_markdown(rich_text_objects)
        return title
