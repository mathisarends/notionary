import re
from typing import override

from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import BlockColor, CreateQuoteBlock, CreateQuoteData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class QuoteParser(LineParser):
    QUOTE_PATTERN = r"^>\s*(.+)$"

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._pattern = re.compile(self.QUOTE_PATTERN)
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_quote(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_quote_block(context.line)
        if block:
            context.result_blocks.append(block)

    def _is_quote(self, line: str) -> bool:
        return self._pattern.match(line.strip()) is not None

    async def _create_quote_block(self, line: str) -> CreateQuoteBlock | None:
        match = self._pattern.match(line.strip())
        if not match:
            return None

        content = match.group(1).strip()
        if not content:
            return None

        # Reject multiline quotes
        if "\n" in content or "\r" in content:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(content)
        quote_data = CreateQuoteData(rich_text=rich_text, color=BlockColor.DEFAULT)

        return CreateQuoteBlock(quote=quote_data)
