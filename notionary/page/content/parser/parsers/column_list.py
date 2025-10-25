from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import BlockCreatePayload, CreateColumnListBlock, CreateColumnListData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class ColumnListParser(LineParser):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_column_list_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_column_list_start(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_column_list_start(context):
            await self._process_column_list(context)

    def _is_column_list_start(self, context: BlockParsingContext) -> bool:
        return self._syntax.regex_pattern.match(context.line) is not None

    async def _process_column_list(self, context: BlockParsingContext) -> None:
        block = self._create_column_list_block()
        await self._populate_columns(block, context)
        context.result_blocks.append(block)

    def _create_column_list_block(self) -> CreateColumnListBlock:
        column_list_data = CreateColumnListData(children=[])
        return CreateColumnListBlock(column_list=column_list_data)

    async def _populate_columns(self, block: CreateColumnListBlock, context: BlockParsingContext) -> None:
        parent_indent_level = context.get_line_indentation_level()
        child_lines = self._collect_children_allowing_empty_lines(context, parent_indent_level)

        if not child_lines:
            return

        column_blocks = await self._parse_column_children(child_lines, context)
        block.column_list.children = column_blocks
        context.lines_consumed = len(child_lines)

    async def _parse_column_children(self, child_lines: list[str], context: BlockParsingContext) -> list:
        stripped_lines = context.strip_indentation_level(child_lines, levels=1)
        child_markdown = "\n".join(stripped_lines)
        parsed_blocks = await context.parse_nested_markdown(child_markdown)
        return self._extract_column_blocks(parsed_blocks)

    def _collect_children_allowing_empty_lines(
        self, context: BlockParsingContext, parent_indent_level: int
    ) -> list[str]:
        child_lines = []
        expected_child_indent = parent_indent_level + 1
        remaining_lines = context.get_remaining_lines()

        for line in remaining_lines:
            if self._should_include_as_child(line, expected_child_indent, context):
                child_lines.append(line)
            else:
                break

        return child_lines

    def _should_include_as_child(self, line: str, expected_indent: int, context: BlockParsingContext) -> bool:
        if not line.strip():
            return True

        line_indent = context.get_line_indentation_level(line)
        return line_indent >= expected_indent

    def _extract_column_blocks(self, blocks: list[BlockCreatePayload]) -> list:
        return [block for block in blocks if self._is_valid_column_block(block)]

    def _is_valid_column_block(self, block: BlockCreatePayload) -> bool:
        return block.type == BlockType.COLUMN and block.column is not None
