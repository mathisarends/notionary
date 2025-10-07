from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.renderers.captioned_block import CaptionedBlockRenderer


class PdfRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.PDF

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_pdf_url(block)

        if not url:
            return ""

        syntax = self._syntax_registry.get_pdf_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_pdf_url(self, block: Block) -> str:
        if not block.pdf:
            return ""

        if block.pdf.external:
            return block.pdf.external.url or ""
        elif block.pdf.file:
            return block.pdf.file.url or ""

        return ""
