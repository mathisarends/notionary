import re
from typing import override

from notionary.blocks.schemas import (
    CreateSyncedBlockBlock,
    CreateSyncedBlockData,
    SyncedFromBlock,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.utils.mixins.logging import LoggingMixin


class SyncedBlockParser(LineParser, LoggingMixin):
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
        if not self._is_duplicate_block(context.line):
            self.logger.warning(
                "Original Synced Blocks (without 'Synced from:') must be created via the Notion UI and can then be referenced by block ID. This parser can only process 'Synced from: <block-id>' references."
            )
            return

        self._process_duplicate_block(context)

    def _is_duplicate_block(self, line: str) -> bool:
        return "Synced from:" in line

    def _process_duplicate_block(self, context: BlockParsingContext) -> None:
        block_id = self._extract_block_id(context.line)
        if not block_id:
            return

        block = self._create_duplicate_synced_block(block_id)
        context.result_blocks.append(block)

    def _create_duplicate_synced_block(self, block_id: str) -> CreateSyncedBlockBlock:
        synced_from = SyncedFromBlock(block_id=block_id)
        synced_data = CreateSyncedBlockData(synced_from=synced_from, children=None)
        return CreateSyncedBlockBlock(synced_block=synced_data)

    def _extract_block_id(self, line: str) -> str | None:
        match = re.search(r"Synced from:\s*([a-f0-9-]+)", line)
        return match.group(1) if match else None
