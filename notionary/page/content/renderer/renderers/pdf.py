from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.file_like_block import FileLikeBlockRenderer
from notionary.page.content.syntax import SyntaxDefinition


class PdfRenderer(FileLikeBlockRenderer):
    @override
    def _get_block_type(self) -> BlockType:
        return BlockType.PDF

    @override
    def _get_syntax(self) -> SyntaxDefinition:
        return self._syntax_registry.get_pdf_syntax()

    @override
    def _get_file_data(self, block: Block) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.pdf

    # Compatibility wrapper expected by some tests — forwards to the shared extractor.
    def _extract_pdf_url(self, block: Block) -> str:
        return self._extract_url(block)
