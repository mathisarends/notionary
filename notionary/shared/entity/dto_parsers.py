from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.shared.entity.schemas import Describable, Titled


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
