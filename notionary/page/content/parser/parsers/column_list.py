from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import BlockCreatePayload, CreateColumnListBlock, CreateColumnListData
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class ColumnListParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_column_list_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_column_list_start(context) or self._is_column_list_end(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_column_list_start(context):
            await self._start_column_list(context)
        elif self._is_column_list_end(context):
            await self._finalize_column_list(context)

    def _is_column_list_start(self, context: BlockParsingContext) -> bool:
        return self._syntax.regex_pattern.match(context.line) is not None

    def _is_column_list_end(self, context: BlockParsingContext) -> bool:
        if not self._syntax.end_regex_pattern.match(context.line):
            return False

        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return isinstance(current_parent.block, CreateColumnListBlock)

    async def _start_column_list(self, context: BlockParsingContext) -> None:
        column_list_data = CreateColumnListData()
        block = CreateColumnListBlock(column_list=column_list_data)

        parent_context = ParentBlockContext(
            block=block,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _finalize_column_list(self, context: BlockParsingContext) -> None:
        column_list_context = context.parent_stack.pop()
        await self._assign_column_list_children(column_list_context, context)

        if context.parent_stack:
            parent_context = context.parent_stack[-1]
            parent_context.add_child_block(column_list_context.block)
        else:
            context.result_blocks.append(column_list_context.block)

    async def _assign_column_list_children(
        self, column_list_context: ParentBlockContext, context: BlockParsingContext
    ) -> None:
        all_children = []

        if column_list_context.child_lines:
            children_text = "\n".join(column_list_context.child_lines)
            text_blocks = await context.parse_nested_content(children_text)
            all_children.extend(text_blocks)

        if column_list_context.child_blocks:
            all_children.extend(column_list_context.child_blocks)

        column_children = self._filter_column_blocks(all_children)
        column_list_context.block.column_list.children = column_children

    def _filter_column_blocks(self, blocks: list[BlockCreatePayload]) -> list:
        return [
            block for block in blocks if block.type == BlockType.COLUMN and hasattr(block, "column") and block.column
        ]
