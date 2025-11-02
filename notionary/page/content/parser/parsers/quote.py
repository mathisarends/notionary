from typing import override

from notionary.blocks.schemas import BlockColor, CreateQuoteBlock, CreateQuoteData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)


class QuoteParser(LineParser):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_converter: MarkdownRichTextConverter,
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_quote_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_quote(context.line)

    def _is_quote(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        quote_lines = self._collect_quote_lines(context)

        block = await self._create_quote_block(quote_lines)
        if not block:
            return

        # Lines consumed: all quote lines minus the current line (which is already being processed)
        context.lines_consumed = len(quote_lines) - 1

        await self._process_nested_children(block, context, quote_lines)
        context.result_blocks.append(block)

    def _collect_quote_lines(self, context: BlockParsingContext) -> list[str]:
        quote_lines = [context.line]
        for line in context.get_remaining_lines():
            if not self._is_quote(line):
                break
            quote_lines.append(line)
        return quote_lines

    async def _process_nested_children(
        self,
        block: CreateQuoteBlock,
        context: BlockParsingContext,
        quote_lines: list[str],
    ) -> None:
        # Calculate indent level after all quote lines
        last_quote_line_index = len(quote_lines) - 1
        child_lines = self._collect_child_lines_after_quote(
            context, last_quote_line_index
        )

        if not child_lines:
            return

        child_blocks = await self._parse_child_blocks(child_lines, context)
        if child_blocks:
            block.quote.children = child_blocks

        context.lines_consumed += len(child_lines)

    def _collect_child_lines_after_quote(
        self, context: BlockParsingContext, last_quote_index: int
    ) -> list[str]:
        """Collect indented children after the quote block."""
        parent_indent_level = context.get_line_indentation_level()
        remaining_lines = context.get_remaining_lines()

        # Skip the quote lines we already processed
        lines_after_quote = remaining_lines[last_quote_index:]

        child_lines = []
        expected_child_indent = parent_indent_level + 1

        for line in lines_after_quote:
            if not line.strip():
                child_lines.append(line)
                continue

            line_indent = context.get_line_indentation_level(line)
            if line_indent >= expected_child_indent:
                child_lines.append(line)
            else:
                break

        return child_lines

    async def _parse_child_blocks(
        self, child_lines: list[str], context: BlockParsingContext
    ) -> list[CreateQuoteBlock]:
        stripped_lines = self._remove_parent_indentation(child_lines, context)
        children_text = self._convert_lines_to_text(stripped_lines)
        return await context.parse_nested_markdown(children_text)

    def _remove_parent_indentation(
        self, lines: list[str], context: BlockParsingContext
    ) -> list[str]:
        return context.strip_indentation_level(lines, levels=1)

    def _convert_lines_to_text(self, lines: list[str]) -> str:
        return "\n".join(lines)

    async def _create_quote_block(
        self, quote_lines: list[str]
    ) -> CreateQuoteBlock | None:
        contents = self._extract_quote_contents(quote_lines)
        if not contents:
            return None

        content = self._join_contents_for_multiline_quote(contents)
        rich_text = await self._convert_to_rich_text(content)
        return self._build_block(rich_text)

    def _extract_quote_contents(self, quote_lines: list[str]) -> list[str]:
        contents = []
        for line in quote_lines:
            match = self._syntax.regex_pattern.match(line)
            if match:
                contents.append(match.group(1).strip())
        return contents

    def _join_contents_for_multiline_quote(self, contents: list[str]) -> str:
        return "\n".join(contents)

    async def _convert_to_rich_text(self, content: str):
        return await self._rich_text_converter.to_rich_text(content)

    def _build_block(self, rich_text) -> CreateQuoteBlock:
        quote_data = CreateQuoteData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateQuoteBlock(quote=quote_data)
