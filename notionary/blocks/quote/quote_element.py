from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.quote.quote_models import CreateQuoteBlock, QuoteBlock
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
from notionary.blocks.block_models import Block
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class QuoteElement(NotionBlockElement):
    """
    Handles conversion between Markdown quotes and Notion quote blocks.

    Markdown quote syntax:
    - [quote](Simple quote text)

    Only single-line quotes without author metadata.
    """

    PATTERN = re.compile(r"^\[quote\]\(([^\n\r]+)\)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        match = cls.PATTERN.match(text.strip())
        return bool(match and match.group(1).strip())

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "quote" and block.quote is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown quote to Notion QuoteBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        content = m.group(1).strip()
        if not content:
            return None

        # Parse inline formatting into rich text objects
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        # Return a typed QuoteBlock
        quote_content = QuoteBlock(rich_text=rich_text, color="default")
        return CreateQuoteBlock(quote=quote_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "quote" or block.quote is None:
            return None
        # extract rich_text
        rich = block.quote.rich_text
        # convert to markdown content
        text = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich]
        )
        if not text.strip():
            return None
        return f"[quote]({text.strip()})"

    @classmethod
    def find_matches(cls, text: str) -> list[tuple[int, int, Any]]:
        matches: list[tuple[int, int, Any]] = []
        for m in cls.PATTERN.finditer(text):
            block = cls.markdown_to_notion(m.group(0))
            if block:
                matches.append((m.start(), m.end(), block))
        return matches

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates blockquotes that visually distinguish quoted text."
            )
            .with_usage_guidelines(
                "Use quotes for quoting external sources or highlighting important statements."
            )
            .with_syntax("[quote](Quote text)")
            .with_examples(
                [
                    "[quote](This is a simple blockquote)",
                    "[quote](Knowledge is power)",
                ]
            )
            .build()
        )
