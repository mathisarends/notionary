from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.quote.quote_models import CreateQuoteBlock, QuoteBlock
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.types import BlockColor


class QuoteElement(BaseBlockElement):
    """
    Handles conversion between Markdown quotes and Notion quote blocks.

    Markdown quote syntax:
    - [quote](Simple quote text)

    Only single-line quotes without author metadata.
    """

    PATTERN = re.compile(r"^\[quote\]\(([^\n\r]+)\)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.QUOTE and block.quote

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown quote to Notion QuoteBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(1).strip()
        if not content:
            return None

        # Parse inline formatting into rich text objects
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        # Return a typed QuoteBlock
        quote_content = QuoteBlock(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateQuoteBlock(quote=quote_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.QUOTE or not block.quote:
            return None

        rich = block.quote.rich_text
        text = TextInlineFormatter.extract_text_with_formatting(rich)

        if not text.strip():
            return None

        return f"[quote]({text.strip()})"
