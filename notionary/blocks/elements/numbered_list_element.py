import re
from typing import Dict, Any, Optional
from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.elements.text_inline_formatter import TextInlineFormatter


class NumberedListElement(NotionBlockElement):
    """Class for converting between Markdown numbered lists and Notion numbered list items."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown numbered list item to Notion block."""
        pattern = re.compile(r"^\s*(\d+)\.\s+(.+)$")
        numbered_match = pattern.match(text)
        if not numbered_match:
            return None

        content = numbered_match.group(2)

        # Use parse_inline_formatting to handle rich text
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        return {
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": rich_text, "color": "default"},
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion numbered list item block to markdown."""
        if block.get("type") != "numbered_list_item":
            return None

        rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        content = TextInlineFormatter.extract_text_with_formatting(rich_text)

        return f"1. {content}"

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r"^\s*\d+\.\s+(.+)$")
        return bool(pattern.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "numbered_list_item"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the numbered list element.
        """
        return (
            ElementPromptBuilder()
            .with_description("Creates numbered list items for ordered sequences.")
            .with_usage_guidelines(
                "Use for lists where order matters, such as steps, rankings, or sequential items."
            )
            .with_syntax("1. Item text")
            .with_standard_markdown()
            .build()
        )
