import re
from typing import Dict, Any, Optional
from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)

from notionary.blocks.elements.text_inline_formatter import TextInlineFormatter


class BulletedListElement(NotionBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown bulleted list item to Notion block."""
        pattern = re.compile(
            r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$"
        )  # Avoid matching todo items
        list_match = pattern.match(text)
        if not list_match:
            return None

        content = list_match.group(2)

        # Use parse_inline_formatting to handle rich text
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich_text, "color": "default"},
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bulleted list item block to markdown."""
        if block.get("type") != "bulleted_list_item":
            return None

        rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        content = TextInlineFormatter.extract_text_with_formatting(rich_text)

        return f"- {content}"

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$")
        return bool(pattern.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "bulleted_list_item"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the bulleted list element.
        """
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
