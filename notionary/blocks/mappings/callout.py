import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType, CalloutData, CreateCalloutBlock
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.shared.models.icon_models import EmojiIcon, Icon


class CalloutMapper(NotionMarkdownMapper):
    PATTERN = re.compile(
        r"^\[callout\]\("  # prefix
        r"([^\"]+?)"  # content
        r"(?:\s+\"([^\"]+)\")?"  # optional emoji
        r"\)$"
    )

    DEFAULT_EMOJI = "💡"
    DEFAULT_COLOR = "gray_background"

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.CALLOUT and block.callout

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateCalloutBlock:
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content, emoji = match.group(1), match.group(2)
        if not content:
            return None

        if not emoji:
            emoji = cls.DEFAULT_EMOJI

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content.strip())

        callout_content = CalloutData(
            rich_text=rich_text,
            icon=EmojiIcon(emoji=emoji),
            color=cls.DEFAULT_COLOR,
        )
        return CreateCalloutBlock(callout=callout_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.CALLOUT or not block.callout:
            return None

        data = block.callout

        converter = RichTextToMarkdownConverter()
        content = await converter.to_markdown(data.rich_text)
        if not content:
            return None

        icon: Icon | None = block.callout.icon
        emoji_char = icon.emoji if isinstance(icon, EmojiIcon) else cls.DEFAULT_EMOJI

        if emoji_char and emoji_char != cls.DEFAULT_EMOJI:
            return f'[callout]({content} "{emoji_char}")'
        return f"[callout]({content})"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for callout blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Callout blocks create highlighted text boxes with optional custom emojis for emphasis",
            syntax_examples=[
                "[callout](This is important information)",
                '[callout](Warning message "⚠️")',
                '[callout](Success message "✅")',
                "[callout](Note with default emoji)",
            ],
            usage_guidelines="Use for highlighting important information, warnings, tips, or notes. Default emoji is 💡. Custom emoji should be provided in quotes after the text content.",
        )
