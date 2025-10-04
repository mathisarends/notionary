import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import (
    Block,
    BlockColor,
    BlockType,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateHeadingBlock,
    Heading1Block,
    Heading2Block,
    Heading3Block,
    HeadingData,
)


class ToggleableHeadingMapper(NotionMarkdownMapper):
    PATTERN = re.compile(r"^[+]{3}(?P<level>#{1,3})\s+(.+)$", re.IGNORECASE)

    @staticmethod
    def match_notion(block: Block) -> bool:
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return False

        # Hier muss auch noch geprüft werden ob das hier auch wirklich toggleable ist (oder man entfernt die toggle logi)
        # Momentan wird das hier so nicht funktionieren
        if isinstance(block, Heading1Block):
            return True

        if isinstance(block, Heading2Block):
            return True

        if isinstance(block, Heading3Block):
            return True

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateHeadingBlock | None:
        """
        Convert markdown collapsible heading to a toggleable Notion HeadingBlock.
        Children are automatically handled by the StackBasedMarkdownConverter.
        """
        if not (match := cls.PATTERN.match(text.strip())):
            return None

        level = len(match.group("level"))  # Count # characters
        content = match.group(2).strip()  # group(2) is the title (no quotes needed)

        if level < 1 or level > 3 or not content:
            return None

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)

        heading_content = HeadingData(rich_text=rich_text, color=BlockColor.DEFAULT, is_toggleable=True, children=[])

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    @staticmethod
    async def notion_to_markdown(block: Block) -> str | None:
        """Convert Notion toggleable heading block to markdown collapsible heading."""
        # Only handle heading blocks via BlockType enum
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return None

        # Determine heading level from enum
        if block.type == BlockType.HEADING_1:
            level = 1
        elif block.type == BlockType.HEADING_2:
            level = 2
        else:
            level = 3

        heading_content = getattr(block, block.type.value)
        if not isinstance(heading_content, HeadingData):
            return None

        converter = RichTextToMarkdownConverter()
        text = await converter.to_markdown(heading_content.rich_text)
        prefix = "#" * level

        return f"+++{prefix} {text or ''}"
