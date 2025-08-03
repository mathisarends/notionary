from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.heading.heading_models import (
    HeadingBlock,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
)
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
from notionary.blocks.block_models import Block
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class ToggleableHeadingElement(NotionBlockElement):
    """
    Simplified ToggleableHeadingElement that works with the stack-based converter.
    Children are automatically handled by the StackBasedMarkdownConverter.
    """

    PATTERN = re.compile(r"^\+(?P<level>#{1,3})\s+(?P<content>.+)$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown collapsible heading."""
        return bool(ToggleableHeadingElement.PATTERN.match(text.strip()))

    @staticmethod
    def match_notion(block: Block) -> bool:
        """Check if block is a Notion toggleable heading."""
        block_type: str = block.type
        if not block_type.startswith("heading_") or block_type[-1] not in "123":
            return False

        # Get the heading content based on block type
        heading_content = block.get_block_content()
        if not heading_content:
            return False

        # Check if it has the is_toggleable property set to true
        return getattr(heading_content, "is_toggleable", False) is True

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown collapsible heading to a toggleable Notion HeadingBlock.
        Children are automatically handled by the StackBasedMarkdownConverter.
        """
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        level = len(match.group("level"))  # Count # characters
        content = match.group("content").strip()

        if level < 1 or level > 3 or not content:
            return None

        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        heading_content = HeadingBlock(
            rich_text=rich_text, color="default", is_toggleable=True, children=[]
        )

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    @staticmethod
    def notion_to_markdown(block: Block) -> Optional[str]:
        """Convert Notion toggleable heading block to markdown collapsible heading."""
        block_type = block.type

        if not block_type.startswith("heading_"):
            return None

        try:
            level = int(block_type[-1])
            if not 1 <= level <= 3:
                return None
        except ValueError:
            return None

        heading_content = block.get_block_content()
        if not heading_content:
            return None

        # Check if it's toggleable
        if not getattr(heading_content, "is_toggleable", False):
            return None

        rich_text = getattr(heading_content, "rich_text", [])
        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        prefix = "#" * level
        return f"+{prefix} {text or ''}"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the collapsible heading element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Collapsible headings combine heading structure with toggleable visibility."
            )
            .with_usage_guidelines(
                "Use when you want to create a structured section that can be expanded or collapsed."
            )
            .with_syntax("+# Collapsible Heading\n| Content with pipe prefix")
            .with_examples(
                [
                    "+# Main Collapsible Section\n| Content under the section",
                    "+## Subsection\n| This content is hidden until expanded",
                    "+### Detailed Information\n| Technical details go here",
                ]
            )
            .build()
        )
