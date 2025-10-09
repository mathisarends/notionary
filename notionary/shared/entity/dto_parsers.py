from typing import cast

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.shared.entity.schemas import Describable, EntityResponseDto, Titled
from notionary.shared.models.cover import CoverType
from notionary.shared.models.icon import IconType
from notionary.shared.models.parent import DatabaseParent, DataSourceParent, ParentType


def extract_emoji_icon_from_dto(entity_dto: EntityResponseDto) -> str | None:
    if not entity_dto.icon or entity_dto.icon.type != IconType.EMOJI:
        return None
    return entity_dto.icon.emoji


def extract_external_icon_url_from_dto(entity_dto: EntityResponseDto) -> str | None:
    if not entity_dto.icon or entity_dto.icon.type != IconType.EXTERNAL:
        return None
    return entity_dto.icon.external.url if entity_dto.icon.external else None


def extract_cover_image_url_from_dto(entity_dto: EntityResponseDto) -> str | None:
    if not entity_dto.cover or entity_dto.cover.type != CoverType.EXTERNAL:
        return None
    return entity_dto.cover.external.url if entity_dto.cover.external else None


def extract_database_id(entity_dto: EntityResponseDto) -> str | None:
    if entity_dto.parent.type == ParentType.DATA_SOURCE_ID:
        data_source_parent = cast(DataSourceParent, entity_dto.parent)
        return data_source_parent.database_id if data_source_parent else None

    if entity_dto.parent.type == ParentType.DATABASE_ID:
        database_parent = cast(DatabaseParent, entity_dto.parent)
        return database_parent.database_id if database_parent else None

    return None


async def extract_title(
    entity: Titled,
    rich_text_converter: RichTextToMarkdownConverter,
) -> str:
    return await rich_text_converter.to_markdown(entity.title)


async def extract_description(
    entity: Describable,
    rich_text_converter: RichTextToMarkdownConverter,
) -> str | None:
    if not entity.description:
        return None
    return await rich_text_converter.to_markdown(entity.description)
