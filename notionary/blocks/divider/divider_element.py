from __future__ import annotations

import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import BlockType
from notionary.blocks.divider.divider_models import CreateDividerBlock, DividerBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class DividerElement(NotionBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.

    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """

    PATTERN = re.compile(r"^\s*-{3,}\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.DIVIDER and block.divider

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown horizontal rule to Notion divider, with preceding empty paragraph."""
        if not cls.PATTERN.match(text.strip()):
            return None

        empty_para = ParagraphBlock(rich_text=[])
        divider = DividerBlock()

        return [
            CreateParagraphBlock(paragraph=empty_para),
            CreateDividerBlock(divider=divider),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.DIVIDER or not block.divider:
            return None
        return "---"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a horizontal divider to separate content sections visually."
            )
            .with_usage_guidelines(
                "Use dividers sparingly to break up sections; only when explicitly requested."
            )
            .with_syntax("---")
            .with_examples(
                ["## Section 1\nContent\n\n---\n\n## Section 2\nMore content"]
            )
            .build()
        )
