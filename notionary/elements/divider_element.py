import re
from typing import Dict, Any, Optional

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class DividerElement(NotionBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.

    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """

    PATTERN = re.compile(r"^\s*-{3,}\s*$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown divider."""
        return bool(DividerElement.PATTERN.match(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion divider."""
        return block.get("type") == "divider"

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown divider to Notion divider block."""
        if not DividerElement.match_markdown(text):
            return None

        return {"type": "divider", "divider": {}}

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion divider block to markdown divider."""
        if block.get("type") != "divider":
            return None

        return "---"

    @staticmethod
    def is_multiline() -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the divider element.
        """
        return {
            "description": "Creates a horizontal divider line that visually separates sections of content.",
            "when_to_use": (
                "Use dividers when you want to create clear visual breaks between different sections or topics in your document. "
                "Dividers help improve readability by organizing content into distinct sections without requiring headings."
            ),
            "syntax": "---",
            "examples": [
                "## Introduction\nThis is the introduction section of the document.\n\n---\n\n## Main Content\nThis is the main content section.",
                "Task List:\n- Complete project proposal\n- Review feedback\n\n---\n\nMeeting Notes:\n- Discussed timeline\n- Assigned responsibilities",
            ],
        }
