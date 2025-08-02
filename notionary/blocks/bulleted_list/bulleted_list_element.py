import re
from typing import Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, RichTextObject
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


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
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        m = cls.PATTERN.match(text)
        if not m:
            return None
        content = m.group(2)
        # parse inline formatting into rich_text objects
        rich_text = TextInlineFormatter.parse_inline_formatting(content)
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich_text, "color": "default"},
        }

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion bulleted list item block to markdown."""
        if block.type != "bulleted_list_item" or block.bulleted_list_item is None:
            return None
        # extract rich_text list of RichTextObject
        rich_list = block.bulleted_list_item.rich_text
        # convert to markdown with inline formatting
        text = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich_list]
        )
        return f"- {text}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

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
