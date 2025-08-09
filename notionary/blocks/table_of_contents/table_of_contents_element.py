from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.block_models import BlockType
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.table_of_contents.table_of_contents_models import (
    CreateTableOfContentsBlock,
    TableOfContentsBlock,
)
from notionary.prompts import ElementPromptBuilder, ElementPromptContent

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult


class TableOfContentsElement(NotionBlockElement):
    """
    Handles conversion between Markdown [toc] syntax and Notion table_of_contents blocks.

    Markdown syntax:
    - [toc]                        → default color
    - [toc](blue)                  → custom color
    - [toc](blue_background)       → custom background color
    """

    PATTERN = re.compile(r"^\[toc\](?:\((?P<color>[a-z_]+)\))?$", re.IGNORECASE)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.TABLE_OF_CONTENTS and block.table_of_contents

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        color = (m.group("color") or "default").lower()
        return CreateTableOfContentsBlock(
            table_of_contents=TableOfContentsBlock(color=color)
        )

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.TABLE_OF_CONTENTS and not block.table_of_contents:
            return None

        color = block.table_of_contents.color
        if color == "default":
            return "[toc]"
        return f"[toc]({color})"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Inserts a dynamic table of contents based on the headings in the page."
            )
            .with_usage_guidelines(
                "Use [toc] to insert a table of contents with default color, "
                "or [toc](color) for a custom color (e.g., blue, blue_background)."
            )
            .with_syntax("[toc] · [toc](blue) · [toc](blue_background)")
            .with_examples(
                [
                    "[toc]",
                    "[toc](gray)",
                    "[toc](blue_background)",
                ]
            )
            .build()
        )
