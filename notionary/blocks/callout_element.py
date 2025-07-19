import re
from typing import Dict, Any, Optional

from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)
from notionary.blocks.text_inline_formatter import TextInlineFormatter
from notionary.blocks.notion_block_element import NotionBlockElement


class CalloutElement(NotionBlockElement):
    """
    Handles conversion between Markdown callouts and Notion callout blocks.

    Markdown callout syntax:
    - !> [emoji] Text - Callout with custom emoji
    - !> Text - Simple callout with default emoji

    Where:
    - [emoji] is any emoji character
    - Text is the callout content with optional inline formatting
    """

    EMOJI_PATTERN = r"(?:\[([^\]]+)\])?\s*"
    TEXT_PATTERN = r"(.+)"

    PATTERN = re.compile(r"^!>\s+" + EMOJI_PATTERN + TEXT_PATTERN + r"$")

    DEFAULT_EMOJI = "💡"
    DEFAULT_COLOR = "gray_background"

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown callout."""
        return text.strip().startswith("!>") and bool(
            CalloutElement.PATTERN.match(text)
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion callout."""
        return block.get("type") == "callout"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown callout to Notion callout block."""
        callout_match = CalloutElement.PATTERN.match(text)
        if not callout_match:
            return None

        emoji = callout_match.group(1)
        content = callout_match.group(2)

        if not emoji:
            emoji = CalloutElement.DEFAULT_EMOJI

        return {
            "type": "callout",
            "callout": {
                "rich_text": TextInlineFormatter.parse_inline_formatting(content),
                "icon": {"type": "emoji", "emoji": emoji},
                "color": CalloutElement.DEFAULT_COLOR,
            },
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion callout block to markdown callout."""
        if block.get("type") != "callout":
            return None

        callout_data = block.get("callout", {})
        rich_text = callout_data.get("rich_text", [])
        icon = callout_data.get("icon", {})

        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        if not text:
            return None

        emoji = ""
        if icon and icon.get("type") == "emoji":
            emoji = icon.get("emoji", "")

        emoji_str = ""
        if emoji and emoji != CalloutElement.DEFAULT_EMOJI:
            emoji_str = f"[{emoji}] "

        return f"!> {emoji_str}{text}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the callout element.
        Includes description, usage guidance, syntax options, and examples.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a callout block to highlight important information with an icon."
            )
            .with_usage_guidelines(
                "Use callouts when you want to draw attention to important information, "
                "tips, warnings, or notes that stand out from the main content. "
                "The emoji MUST be enclosed in square brackets to properly display."
            )
            .with_syntax("!> [emoji] Text")
            .with_examples(
                [
                    "!> [💡] This is a default callout with the light bulb emoji",
                    "!> [🔔] This is a callout with a bell emoji",
                    "!> [⚠️] Warning: This is an important note to pay attention to",
                    "!> [💡] Tip: Add emoji that matches your content's purpose",
                ]
            )
            .with_avoidance_guidelines(
                "NEVER omit the square brackets around the emoji. The format MUST be !> [emoji] and not !> emoji. "
                "Without the square brackets, Notion will not properly render the callout with the specified emoji."
            )
            .build()
        )
