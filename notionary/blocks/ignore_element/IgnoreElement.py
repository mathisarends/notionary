from __future__ import annotations
import re
from notionary.blocks.block_models import Block, BlockCreateResult
from notionary.blocks.notion_block_element import NotionBlockElement



class IgnoreElement(NotionBlockElement):
    """
    Handles container end tags and other lines that should be ignored.
    Prevents them from being processed as paragraphs.
    """

    IGNORE_PATTERNS = [
        re.compile(r"^:::\s*$"),
        re.compile(r"^\|\s*:::\s*$"),
        re.compile(r"^\|\s*$"),
    ]

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text should be ignored."""
        stripped = text.strip()
        return any(pattern.match(stripped) for pattern in cls.IGNORE_PATTERNS)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """This element doesn't produce Notion blocks."""
        return False

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Return None to ignore this line completely."""
        return None

    @classmethod
    def notion_to_markdown(cls, block: Block) -> str:
        """This element doesn't handle Notion blocks."""
        return ""