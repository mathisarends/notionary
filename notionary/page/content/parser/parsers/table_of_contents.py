from typing import override

from notionary.blocks.schemas import BlockColor, CreateTableOfContentsBlock, TableOfContentsData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class TableOfContentsParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_table_of_contents_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_toc(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = self._create_toc_block()
        context.result_blocks.append(block)

    def _is_toc(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    def _create_toc_block(self) -> CreateTableOfContentsBlock:
        toc_data = TableOfContentsData(color=BlockColor.DEFAULT)
        return CreateTableOfContentsBlock(table_of_contents=toc_data)
