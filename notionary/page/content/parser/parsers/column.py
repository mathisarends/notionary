from typing import override

from notionary.blocks.schemas import CreateColumnBlock, CreateColumnData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class ColumnParser(LineParser):
    MIN_WIDTH_RATIO = 0
    MAX_WIDTH_RATIO = 1.0

    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_column_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_column_start(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_column_start(context):
            await self._process_column(context)

    def _is_column_start(self, context: BlockParsingContext) -> bool:
        return self._syntax.regex_pattern.match(context.line) is not None

    async def _process_column(self, context: BlockParsingContext) -> None:
        block = self._create_column_block(context.line)
        if not block:
            return

        await self._populate_children(block, context)
        context.result_blocks.append(block)

    def _create_column_block(self, line: str) -> CreateColumnBlock | None:
        match = self._syntax.regex_pattern.match(line)
        if not match:
            return None

        width_ratio = self._parse_width_ratio(match.group(1))
        column_data = CreateColumnData(width_ratio=width_ratio, children=[])

        return CreateColumnBlock(column=column_data)

    def _parse_width_ratio(self, ratio_str: str | None) -> float | None:
        if not ratio_str:
            return None

        try:
            width_ratio = float(ratio_str)
            return width_ratio if self._is_valid_width_ratio(width_ratio) else None
        except ValueError:
            return None

    def _is_valid_width_ratio(self, width_ratio: float) -> bool:
        return self.MIN_WIDTH_RATIO < width_ratio <= self.MAX_WIDTH_RATIO

    async def _populate_children(
        self, block: CreateColumnBlock, context: BlockParsingContext
    ) -> None:
        parent_indent_level = context.get_line_indentation_level()
        child_lines = context.collect_indented_child_lines(parent_indent_level)

        if not child_lines:
            return

        child_blocks = await self._parse_indented_children(child_lines, context)
        block.column.children = child_blocks
        context.lines_consumed = len(child_lines)

    async def _parse_indented_children(
        self, child_lines: list[str], context: BlockParsingContext
    ) -> list:
        stripped_lines = context.strip_indentation_level(child_lines, levels=1)
        child_markdown = "\n".join(stripped_lines)
        return await context.parse_nested_markdown(child_markdown)
