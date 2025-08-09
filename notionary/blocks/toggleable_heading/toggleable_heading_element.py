from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.heading.heading_models import (
    HeadingBlock,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
)
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
from notionary.blocks.block_models import Block, BlockType
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
        # Use BlockType enum for matching heading blocks
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return False

        if block.heading_1 and block.heading_1.is_toggleable:
            return True
        if block.heading_2 and block.heading_2.is_toggleable:
            return True
        if block.heading_3 and block.heading_3.is_toggleable:
            return True

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
        # Only handle heading blocks via BlockType enum
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return None

        # Determine heading level from enum
        if block.type == BlockType.HEADING_1:
            level = 1
        elif block.type == BlockType.HEADING_2:
            level = 2
        else:
            level = 3

        heading_content = getattr(block, block.type.value)
        if not isinstance(heading_content, HeadingBlock):
            return None

        text = TextInlineFormatter.extract_text_with_formatting(
            heading_content.rich_text
        )
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
