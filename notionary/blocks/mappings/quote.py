import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockColor, BlockType, CreateQuoteBlock, CreateQuoteData


class QuoteMapper(NotionMarkdownMapper):
    PATTERN = re.compile(r"^>\s*(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.QUOTE and block.quote

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateQuoteBlock:
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(1).strip()
        if not content:
            return None

        # Reject multiline quotes
        if "\n" in content or "\r" in content:
            return None

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)

        quote_content = CreateQuoteData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateQuoteBlock(quote=quote_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.QUOTE or not block.quote:
            return None

        rich = block.quote.rich_text
        converter = RichTextToMarkdownConverter()
        text = await converter.to_markdown(rich)

        if not text.strip():
            return None

        return f"> {text.strip()}"
