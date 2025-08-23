from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.breadcrumbs.breadcrumb_models import (
    BreadcrumbBlock,
    CreateBreadcrumbBlock,
)
from notionary.blocks.models import Block, BlockCreateResult, BlockType


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
        # Kein extra Payload – nur Typ prüfen
        return block.type == BlockType.BREADCRUMB and block.breadcrumb

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        if not cls.PATTERN.match(text.strip()):
            return None
        return CreateBreadcrumbBlock(breadcrumb=BreadcrumbBlock())

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type == BlockType.BREADCRUMB and block.breadcrumb:
            return cls.BREADCRUMB_MARKER
