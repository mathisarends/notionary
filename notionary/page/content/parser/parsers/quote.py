import re
from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import BlockColor, CreateQuoteBlock, CreateQuoteData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class QuoteParser(LineParser):
    QUOTE_PATTERN = r"^>(?!>)\s*(.+)$"

    def __init__(self, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__()
        self._pattern = re.compile(self.QUOTE_PATTERN)
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_quote(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        quote_lines = self._collect_quote_lines(context)
        lines_consumed = len(quote_lines)

        block = await self._create_quote_block(quote_lines)
        if block:
            context.result_blocks.append(block)
            context.lines_consumed = lines_consumed

    def _collect_quote_lines(self, context: BlockParsingContext) -> list[str]:
        quote_lines = [context.line]
        for line in context.get_remaining_lines():
            if not self._is_quote(line):
                break
            quote_lines.append(line)
        return quote_lines

    def _is_quote(self, line: str) -> bool:
        return self._pattern.match(line) is not None

    async def _create_quote_block(self, quote_lines: list[str]) -> CreateQuoteBlock | None:
        if not quote_lines:
            return None

        contents = []
        for line in quote_lines:
            match = self._pattern.match(line)
            if match:
                contents.append(match.group(1).strip())

        if not contents:
            return None

        content = self._join_contents_for_multiline_quote(contents)

        rich_text = await self._rich_text_converter.to_rich_text(content)
        quote_data = CreateQuoteData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateQuoteBlock(quote=quote_data)

    def _join_contents_for_multiline_quote(self, contents: list[str]) -> str:
        return "\n".join(contents)
