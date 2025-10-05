import re
from typing import override

from notionary.blocks.schemas import BlockColor, CreateTableOfContentsBlock, TableOfContentsData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class TableOfContentsParser(LineParser):
    TOC_PATTERN = r"^\[toc\]$"

    def __init__(self) -> None:
        super().__init__()
        self._pattern = re.compile(self.TOC_PATTERN, re.IGNORECASE)

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
        return self._pattern.match(line.strip()) is not None

    def _create_toc_block(self) -> CreateTableOfContentsBlock:
        toc_data = TableOfContentsData(color=BlockColor.DEFAULT)
        return CreateTableOfContentsBlock(table_of_contents=toc_data)
