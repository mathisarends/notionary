from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.toggle.toggle_models import CreateToggleBlock, ToggleBlock
from notionary.prompts import (
    ElementPromptContent,
    ElementPromptBuilder,
)
from notionary.blocks.block_models import (
    Block,
)
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class ToggleElement(NotionBlockElement):
    """
    Simplified ToggleElement class that works with the stack-based converter.
    Children are automatically handled by the StackBasedMarkdownConverter.
    """

    TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+(.+)$")
    TRANSCRIPT_TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+Transcript$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if the text is a markdown toggle."""
        return bool(cls.TOGGLE_PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if the block is a Notion toggle block."""
        return block.type == "toggle"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown toggle line to Notion ToggleBlock.
        Children are automatically handled by the StackBasedMarkdownConverter.
        """
        match = cls.TOGGLE_PATTERN.match(text.strip())
        if not match:
            return None

        title = match.group(1).strip()
        rich_text = TextInlineFormatter.parse_inline_formatting(title)

        # Create toggle block with empty children - they will be populated automatically
        toggle_content = ToggleBlock(rich_text=rich_text, color="default", children=[])

        return CreateToggleBlock(toggle=toggle_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """
        Converts a Notion toggle block into markdown using pipe-prefixed lines.
        """
        if block.type != "toggle":
            return None

        if not block.toggle:
            return None

        toggle_data = block.toggle

        # Extract title from rich_text
        title = cls._extract_text_content(toggle_data.rich_text or [])

        # Create toggle line
        toggle_line = f"+++ {title}"

        # Process children if available
        children = toggle_data.children or []
        if not children:
            return toggle_line

        # Add a placeholder line for each child using pipe syntax
        child_lines = ["| [Nested content]" for _ in children]

        return toggle_line + "\n" + "\n".join(child_lines)

    @classmethod
    def _extract_text_content(cls, rich_text: list[RichTextObject]) -> str:
        """Extracts plain text content from Notion rich_text blocks."""
        result = ""
        for text_obj in rich_text:
            if hasattr(text_obj, "plain_text"):
                result += text_obj.plain_text or ""
            elif (
                hasattr(text_obj, "type")
                and text_obj.type == "text"
                and hasattr(text_obj, "text")
            ):
                result += text_obj.text.content or ""
            # Fallback for dict-style access (backward compatibility)
            elif isinstance(text_obj, dict):
                if text_obj.get("type") == "text":
                    result += text_obj.get("text", {}).get("content", "")
                elif "plain_text" in text_obj:
                    result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the toggle element with pipe syntax examples.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Toggle elements are collapsible sections that help organize and hide detailed information."
            )
            .with_usage_guidelines(
                "Use toggles for supplementary information that's not essential for the first reading, "
                "such as details, examples, or technical information."
            )
            .with_syntax("+++ Toggle Title\n| Toggle content with pipe prefix")
            .with_examples(
                [
                    "+++ Key Findings\n| The research demonstrates **three main conclusions**:\n| 1. First important point\n| 2. Second important point",
                    "+++ FAQ\n| **Q: When should I use toggles?**\n| *A: Use toggles for supplementary information.*",
                ]
            )
            .build()
        )
