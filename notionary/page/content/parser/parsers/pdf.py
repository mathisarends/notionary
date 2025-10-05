"""Parser for PDF blocks."""

import re
from typing import override

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import (
    CreatePdfBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class PdfParser(LineParser):
    """Handles PDF blocks with [pdf](url) syntax."""

    PDF_PATTERN = re.compile(r"\[pdf\]\(([^)]+)\)")
    CAPTION_PATTERN = re.compile(r"\(caption:([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.PDF_PATTERN.search(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_pdf_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_pdf_block(self, text: str) -> CreatePdfBlock | None:
        """Create a PDF block from markdown text."""
        pdf_path = self._extract_pdf_path(text.strip())
        if not pdf_path:
            return None

        # Extract caption
        caption_text = self._extract_caption(text.strip())
        caption_rich_text = self._build_caption_rich_text(caption_text or "")

        # Only support external URLs
        pdf_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=pdf_path),
            caption=caption_rich_text,
        )

        return CreatePdfBlock(pdf=pdf_data)

    def _extract_pdf_path(self, text: str) -> str | None:
        """Extract PDF path/URL from text, handling caption patterns."""
        clean_text = self._remove_caption(text)
        match = self.PDF_PATTERN.search(clean_text)
        return match.group(1).strip() if match else None

    def _extract_caption(self, text: str) -> str | None:
        """Extract caption text from markdown."""
        caption_match = self.CAPTION_PATTERN.search(text)
        return caption_match.group(1) if caption_match else None

    def _remove_caption(self, text: str) -> str:
        """Remove caption pattern from text."""
        return self.CAPTION_PATTERN.sub("", text).strip()

    def _build_caption_rich_text(self, caption: str) -> list[RichText]:
        """Build rich text list from caption string."""
        if not caption or not caption.strip():
            return []
        return [RichText.from_plain_text(caption.strip())]
