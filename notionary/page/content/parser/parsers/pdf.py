"""Parser for PDF blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreatePdfBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.captioned_block_parser import (
    CaptionedBlockParser,
)


class PdfParser(CaptionedBlockParser):
    PDF_PATTERN = re.compile(r"\[pdf\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.PDF_PATTERN.search(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        caption_rich_text = await self._extract_caption_for_single_line_block(context)

        pdf_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )
        block = CreatePdfBlock(pdf=pdf_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.PDF_PATTERN.search(line.strip())
        return match.group(1).strip() if match else None
