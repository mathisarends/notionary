import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.schemas import (
    Block,
    BlockCreateResult,
    BlockType,
    BreadcrumbBlock,
    CreateBreadcrumbBlock,
)


class BreadcrumbElement(BaseBlockElement):
    """
    Handles conversion between Markdown breadcrumb marker and Notion breadcrumb blocks.

    Markdown syntax:
      [breadcrumb]
    """

    BREADCRUMB_MARKER = "[breadcrumb]"
    PATTERN = re.compile(r"^\[breadcrumb\]\s*$", re.IGNORECASE)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.BREADCRUMB and block.breadcrumb

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        if not cls.PATTERN.match(text.strip()):
            return None
        return CreateBreadcrumbBlock(breadcrumb=BreadcrumbBlock())

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type == BlockType.BREADCRUMB and block.breadcrumb:
            return cls.BREADCRUMB_MARKER
