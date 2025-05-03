import re
from typing import Dict, Any, Optional

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent
from notionary.elements.text_inline_formatter import TextInlineFormatter


class HeadingElement(NotionBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""

    PATTERN = re.compile(r"^(#{1,3})\s(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown heading."""
        return bool(HeadingElement.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion heading."""
        block_type: str = block.get("type", "")
        return block_type.startswith("heading_") and block_type[-1] in "123"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown heading to Notion heading block."""
        header_match = HeadingElement.PATTERN.match(text)
        if not header_match:
            return None

        level = len(header_match.group(1))
        if not 1 <= level <= 3:
            return None

        content = header_match.group(2)

        return {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": TextInlineFormatter.parse_inline_formatting(content)
            },
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion heading block to markdown heading."""
        block_type = block.get("type", "")

        if not block_type.startswith("heading_"):
            return None

        try:
            level = int(block_type[-1])
            # Only allow levels 1-3
            if not 1 <= level <= 3:
                return None
        except ValueError:
            return None

        heading_data = block.get(block_type, {})
        rich_text = heading_data.get("rich_text", [])

        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        prefix = "#" * level
        return f"{prefix} {text or ''}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the heading element.
        """
        return {
            "description": "Use Markdown headings (#, ##, ###) to structure content hierarchically.",
            "when_to_use": "Use to group content into sections and define a visual hierarchy.",
            "syntax": "## Your Heading Text",
            "examples": [
                "# Main Title",
                "## Section Title",
                "### Subsection Title",
            ],
        }
