from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.callout.callout_models import (
    CalloutBlock,
    CreateCalloutBlock,
    EmojiIcon,
    IconObject,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class CalloutElement(BaseBlockElement):
    """
    Handles conversion between Markdown callouts and Notion callout blocks.

    Markdown callout syntax:
    - [callout](Text) - Simple callout with default emoji
    - [callout](Text "emoji") - Callout with custom emoji

    Where:
    - Text is the required callout content
    - emoji is an optional emoji character (enclosed in quotes)
    """

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
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert a markdown callout into a Notion CalloutBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content, emoji = match.group(1), match.group(2)
        if not content:
            return None

        if not emoji:
            emoji = cls.DEFAULT_EMOJI

        rich_text = TextInlineFormatter.parse_inline_formatting(content.strip())

        callout_content = CalloutBlock(
            rich_text=rich_text,
            icon=EmojiIcon(emoji=emoji),
            color=cls.DEFAULT_COLOR,
        )
        return CreateCalloutBlock(callout=callout_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.CALLOUT or not block.callout:
            return None

        data = block.callout

        content = TextInlineFormatter.extract_text_with_formatting(data.rich_text)
        if not content:
            return None

        icon: Optional[IconObject] = block.callout.icon
        emoji_char = icon.emoji if isinstance(icon, EmojiIcon) else cls.DEFAULT_EMOJI

        if emoji_char and emoji_char != cls.DEFAULT_EMOJI:
            return f'[callout]({content} "{emoji_char}")'
        return f"[callout]({content})"

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
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
