from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.table_of_contents.table_of_contents_models import (
    CreateTableOfContentsBlock,
    TableOfContentsBlock,
)
from notionary.blocks.types import BlockType


class TableOfContentsElement(BaseBlockElement):
    """
    Handles conversion between Markdown [toc] syntax and Notion table_of_contents blocks.

    Markdown syntax:
    - [toc]                        → default color
    - [toc](blue)                  → custom color
    - [toc](blue_background)       → custom background color
    """

    PATTERN = re.compile(r"^\[toc\](?:\((?P<color>[a-z_]+)\))?$", re.IGNORECASE)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.TABLE_OF_CONTENTS and block.table_of_contents

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        if not (input_match := cls.PATTERN.match(text.strip())):
            return None

        color = (input_match.group("color") or "default").lower()
        return CreateTableOfContentsBlock(
            table_of_contents=TableOfContentsBlock(color=color)
        )

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        # Fix: Use 'or' instead of 'and'
        if block.type != BlockType.TABLE_OF_CONTENTS or not block.table_of_contents:
            return None

        color = block.table_of_contents.color.value

        if color == "default":
            return "[toc]"
        return f"[toc]({color})"

    @classmethod
    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for table of contents blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Table of contents blocks automatically generate navigation for page headings",
            syntax_examples=[
                "[toc]",
                "[toc](blue)",
                "[toc](blue_background)",
                "[toc](gray_background)",
            ],
            usage_guidelines="Use to automatically generate a clickable table of contents from page headings. Optional color parameter changes the appearance. Default color is gray.",
        )
