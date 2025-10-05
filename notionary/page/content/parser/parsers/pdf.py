"""Parser for PDF blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreatePdfBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser


class PdfParser(LineParser):
    PDF_PATTERN = re.compile(r"\[pdf\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.PDF_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        pdf_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=[],
        )
        block = CreatePdfBlock(pdf=pdf_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.PDF_PATTERN.search(line)
        return match.group(1).strip() if match else None
