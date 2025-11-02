import re
from typing import override

from notionary.blocks.schemas import (
    BlockCreatePayload,
    CreateSyncedBlockBlock,
    CreateSyncedBlockData,
    SyncedFromBlock,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


# TODO: Test this shit here
class SyncedBlockParser(LineParser):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_synced_block_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.match(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_duplicate_block(context.line):
            self._process_duplicate_block(context)
        else:
            await self._process_original_block(context)

    def _is_duplicate_block(self, line: str) -> bool:
        return "Synced from:" in line and self._syntax.end_regex_pattern.search(line)

    def _process_duplicate_block(self, context: BlockParsingContext) -> None:
        block_id = self._extract_block_id(context.line)
        if not block_id:
            return

        block = self._create_duplicate_synced_block(block_id)
        context.result_blocks.append(block)

    async def _process_original_block(self, context: BlockParsingContext) -> None:
        block = self._create_original_synced_block()
        await self._populate_children(block, context)
        context.result_blocks.append(block)

    def _create_duplicate_synced_block(self, block_id: str) -> CreateSyncedBlockBlock:
        synced_from = SyncedFromBlock(block_id=block_id)
        synced_data = CreateSyncedBlockData(synced_from=synced_from, children=None)
        return CreateSyncedBlockBlock(synced_block=synced_data)

    def _create_original_synced_block(self) -> CreateSyncedBlockBlock:
        synced_data = CreateSyncedBlockData(synced_from=None, children=[])
        return CreateSyncedBlockBlock(synced_block=synced_data)

    async def _populate_children(
        self, block: CreateSyncedBlockBlock, context: BlockParsingContext
    ) -> None:
        parent_indent_level = context.get_line_indentation_level()
        child_lines = self._collect_block_content(context, parent_indent_level)

        if not child_lines:
            return

        child_lines = self._remove_trailing_empty_lines(child_lines)

        if not child_lines:
            return

        child_blocks = await self._parse_children(child_lines, context)
        block.synced_block.children = child_blocks

    def _collect_block_content(
        self, context: BlockParsingContext, parent_indent_level: int
    ) -> list[str]:
        child_lines = []
        lines_consumed = 0
        remaining_lines = context.get_remaining_lines()

        for line in remaining_lines:
            lines_consumed += 1

            # Check if we hit the end delimiter
            if self._syntax.end_regex_pattern.match(line.strip()):
                break

            child_lines.append(line)

        context.lines_consumed = lines_consumed
        return child_lines

    async def _parse_children(
        self, child_lines: list[str], context: BlockParsingContext
    ) -> list[BlockCreatePayload]:
        stripped_lines = context.strip_indentation_level(child_lines, levels=1)
        child_markdown = "\n".join(stripped_lines)
        return await context.parse_nested_markdown(child_markdown)

    def _extract_block_id(self, line: str) -> str | None:
        match = re.search(r"Synced from:\s*([a-f0-9-]+)", line)
        return match.group(1) if match else None

    def _remove_trailing_empty_lines(self, lines: list[str]) -> list[str]:
        while lines and not lines[-1].strip():
            lines.pop()
        return lines
