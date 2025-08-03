from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import (
    Block,
)
from notionary.blocks.callout.callout_models import CalloutBlock, CreateCalloutBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.models.icon_types import EmojiIcon, IconObject
from notionary.prompts import ElementPromptContent, ElementPromptBuilder


class CalloutElement(NotionBlockElement):
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
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "callout" and block.callout is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert a markdown callout into a Notion CalloutBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        content, emoji = m.group(1), m.group(2)
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
        if block.type != "callout" or block.callout is None:
            return None

        data = block.callout
        # extract formatted content
        content = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in data.rich_text]
        )
        if not content:
            return None
        # determine emoji
        icon: IconObject = block.callout.icon  # IconObject union type
        emoji_char = cls._get_emoji(icon)
        if emoji_char and emoji_char != cls.DEFAULT_EMOJI:
            return f'[callout]({content} "{emoji_char}")'
        return f"[callout]({content})"

    @classmethod
    def _get_emoji(cls, icon: IconObject) -> str:
        if hasattr(icon, "emoji"):
            return icon.emoji or ""
        return ""

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a callout block highlighting important info with an optional icon."
            )
            .with_usage_guidelines(
                "Use callouts for warnings, tips, notes or any content that needs emphasis."
            )
            .with_syntax('[callout](Text content "Optional emoji")')
            .with_examples(
                [
                    "[callout](Note this important point)",
                    '[callout](Remember to save your work "💾")',
                    '[callout](Warning: data loss possible "⚠️")',
                ]
            )
            .build()
        )
