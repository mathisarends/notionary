from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.breadcrumbs.breadcrumb_models import BreadcrumbBlock, CreateBreadcrumbBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
from notionary.blocks.block_models import Block, BlockType



if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateResult


class BreadcrumbElement(NotionBlockElement):
    """
    Handles conversion between Markdown breadcrumb marker and Notion breadcrumb blocks.

    Markdown syntax:
      [breadcrumb]
    """

    BREADCRUMB_MARKER = "[breadcrumb]"
    PATTERN = re.compile(r"^\[breadcrumb\]\s*$", re.IGNORECASE)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Kein extra Payload – nur Typ prüfen
        return block.type == BlockType.BREADCRUMB and block.breadcrumb

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        if not cls.match_markdown(text):
            return None
        return CreateBreadcrumbBlock(breadcrumb=BreadcrumbBlock())

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type == BlockType.BREADCRUMB and block.breadcrumb:
            return cls.BREADCRUMB_MARKER

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Inserts a breadcrumb block that shows the page hierarchy.")
            .with_syntax(cls.BREADCRUMB_MARKER)
            .with_examples([cls.BREADCRUMB_MARKER])
            .build()
        )
