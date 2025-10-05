"""Parser for file blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreateFileBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser


class FileParser(LineParser):
    FILE_PATTERN = re.compile(r"\[file\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.FILE_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        file_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=[],
        )
        block = CreateFileBlock(file=file_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.FILE_PATTERN.search(line)
        return match.group(1).strip() if match else None
