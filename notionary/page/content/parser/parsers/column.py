import re
from typing import override

from notionary.blocks.schemas import CreateColumnBlock, CreateColumnData, CreateColumnListBlock
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class ColumnParser(LineParser):
    COLUMN_START_PATTERN = r"^:::\s*column(?:\s+(0?\.\d+|1(?:\.0?)?))??\s*$"
    COLUMN_END_PATTERN = r"^:::\s*$"
    MIN_WIDTH_RATIO = 0
    MAX_WIDTH_RATIO = 1.0

    def __init__(self) -> None:
        super().__init__()
        self._start_pattern = re.compile(self.COLUMN_START_PATTERN, re.IGNORECASE)
        self._end_pattern = re.compile(self.COLUMN_END_PATTERN)

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_column_start(context) or self._is_column_end(context) or self._is_column_content(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_column_start(context):
            await self._start_column(context)
        elif self._is_column_end(context):
            await self._finalize_column(context)
        elif self._is_column_content(context):
            await self._add_column_content(context)

    def _is_column_start(self, context: BlockParsingContext) -> bool:
        return self._start_pattern.match(context.line) is not None

    def _is_column_end(self, context: BlockParsingContext) -> bool:
        if not self._end_pattern.match(context.line):
            return False

        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return isinstance(current_parent.block, CreateColumnBlock)

    def _is_column_content(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not isinstance(current_parent.block, CreateColumnBlock):
            return False

        line = context.line.strip()
        return not (self._start_pattern.match(line) or self._end_pattern.match(line))

    async def _add_column_content(self, context: BlockParsingContext) -> None:
        context.parent_stack[-1].add_child_line(context.line)

    async def _start_column(self, context: BlockParsingContext) -> None:
        block = self._create_column_block(context.line)
        if not block:
            return

        parent_context = ParentBlockContext(
            block=block,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _create_column_block(self, line: str) -> CreateColumnBlock | None:
        match = self._start_pattern.match(line)
        if not match:
            return None

        width_ratio = self._parse_width_ratio(match.group(1))
        column_data = CreateColumnData(width_ratio=width_ratio)

        return CreateColumnBlock(column=column_data)

    def _parse_width_ratio(self, ratio_str: str | None) -> float | None:
        if not ratio_str:
            return None

        try:
            width_ratio = float(ratio_str)
            return width_ratio if self.MIN_WIDTH_RATIO < width_ratio <= self.MAX_WIDTH_RATIO else None
        except ValueError:
            return None

    async def _finalize_column(self, context: BlockParsingContext) -> None:
        column_context = context.parent_stack.pop()
        await self._assign_column_children(column_context, context)

        if self._has_column_list_parent(context):
            parent = context.parent_stack[-1]
            parent.add_child_block(column_context.block)
        else:
            context.result_blocks.append(column_context.block)

    def _has_column_list_parent(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False
        return isinstance(context.parent_stack[-1].block, CreateColumnListBlock)

    async def _assign_column_children(self, column_context: ParentBlockContext, context: BlockParsingContext) -> None:
        all_children = []

        if column_context.child_lines:
            children_text = "\n".join(column_context.child_lines)
            text_blocks = await context.parse_nested_content(children_text)
            all_children.extend(text_blocks)

        if column_context.child_blocks:
            all_children.extend(column_context.child_blocks)

        column_context.block.column.children = all_children
