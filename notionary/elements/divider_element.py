import re
from typing import Dict, Any, Optional

from notionary.elements.notion_block_element import NotionBlockElement, auto_track_conversions
from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)

@auto_track_conversions
class DividerElement(NotionBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.

    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """

    PATTERN = re.compile(r"^\s*-{3,}\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown divider."""
        return bool(DividerElement.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion divider."""
        return block.get("type") == "divider"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown divider to Notion divider block."""
        if not DividerElement.match_markdown(text):
            return None

        return {"type": "divider", "divider": {}}

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion divider block to markdown divider."""
        if block.get("type") != "divider":
            return None

        return "---"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns structured LLM prompt metadata for the divider element."""
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a horizontal divider line to visually separate sections of content."
            )
            .with_usage_guidelines(
                "Use dividers only sparingly and only when the user explicitly asks for them. Dividers create strong visual breaks between content sections, so they should not be used unless specifically requested by the user."
            )
            .with_syntax("---")
            .with_examples(
                ["## Section 1\nContent\n\n---\n\n## Section 2\nMore content"]
            )
            .build()
        )
