import re
from typing import Dict, Any, Optional, List

from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter
from notionary.blocks import (
    NotionBlockElement,
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)


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

    # Regex pattern for callout syntax with optional emoji
    PATTERN = re.compile(
        r"^\[callout\]\("  # [callout]( prefix
        + r'([^"]+?)'  # Text content (required)
        + r'(?:\s+"([^"]+)")?'  # Optional emoji in quotes
        + r"\)$"  # closing parenthesis
    )

    # Default values
    DEFAULT_EMOJI = "💡"
    DEFAULT_COLOR = "gray_background"

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown callout."""
        return text.strip().startswith("[callout]") and bool(
            CalloutElement.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion callout."""
        return block.get("type") == "callout"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown callout to Notion callout block."""
        callout_match = CalloutElement.PATTERN.match(text.strip())
        if not callout_match:
            return None

        content = callout_match.group(1)
        emoji = callout_match.group(2)

        if not content:
            return None

        # Use default emoji if none provided
        if not emoji:
            emoji = CalloutElement.DEFAULT_EMOJI

        callout_data = {
            "rich_text": TextInlineFormatter.parse_inline_formatting(content.strip()),
            "icon": {"type": "emoji", "emoji": emoji},
            "color": CalloutElement.DEFAULT_COLOR,
        }

        return {"type": "callout", "callout": callout_data}

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion callout block to markdown callout."""
        if block.get("type") != "callout":
            return None

        callout_data = block.get("callout", {})
        rich_text = callout_data.get("rich_text", [])
        icon = callout_data.get("icon", {})

        content = TextInlineFormatter.extract_text_with_formatting(rich_text)
        if not content:
            return None

        emoji = CalloutElement._extract_emoji(icon)

        if emoji and emoji != CalloutElement.DEFAULT_EMOJI:
            return f'[callout]({content} "{emoji}")'

        return f"[callout]({content})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Callouts are single-line elements."""
        return False

    @classmethod
    def _extract_emoji(cls, icon: Dict[str, Any]) -> str:
        """Extract emoji from Notion icon object."""
        if icon and icon.get("type") == "emoji":
            return icon.get("emoji", "")
        return ""

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the callout element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a callout block to highlight important information with an icon."
            )
            .with_usage_guidelines(
                "Use callouts when you want to draw attention to important information, "
                "tips, warnings, or notes that stand out from the main content."
            )
            .with_syntax('[callout](Text content "Optional emoji")')
            .with_examples(
                [
                    "[callout](This is a default callout with the light bulb emoji)",
                    '[callout](This is a callout with a bell emoji "🔔")',
                    '[callout](Warning: This is an important note "⚠️")',
                    '[callout](Tip: Add emoji that matches your content\'s purpose "💡")',
                ]
            )
            .build()
        )
