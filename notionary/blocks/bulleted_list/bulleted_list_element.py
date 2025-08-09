from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.rich_text.rich_text_models import RichTextObject

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.bulleted_list.bulleted_list_models import (
    BulletedListItemBlock,
    CreateBulletedListItemBlock,
)
from notionary.blocks.block_models import Block
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class BulletedListElement(NotionBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""

    # Regex for markdown bullets (excluding todo items [ ] or [x])
    PATTERN = re.compile(r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.rstrip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return (
            block.type == "bulleted_list_item" and block.bulleted_list_item is not None
        )

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert a markdown bulleted list item into a Notion BulletedListItemBlock.
        """
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        # Extract the content part (second capture group)
        content = m.group(2)

        # Parse inline markdown formatting into RichTextObject list
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        # Return a properly typed Notion block
        bulleted_list_content = BulletedListItemBlock(
            rich_text=rich_text, color="default"
        )
        return CreateBulletedListItemBlock(bulleted_list_item=bulleted_list_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion bulleted_list_item block to Markdown."""
        if block.type != "bulleted_list_item" or not block.bulleted_list_item:
            return None

        rich_list = block.bulleted_list_item.rich_text
        if not rich_list:
            return "-"

        text = TextInlineFormatter.extract_text_with_formatting(rich_list)
        return f"- {text}"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Creates bulleted list items for unordered lists.")
            .with_usage_guidelines(
                "Use for lists where order doesn't matter, such as features, options, or items without hierarchy."
            )
            .with_syntax("- Item text")
            .with_standard_markdown()
            .build()
        )
