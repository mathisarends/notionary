from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.file_like_block import FileLikeBlockRenderer
from notionary.page.content.syntax.definition import EnclosedSyntaxDefinition


class PdfRenderer(FileLikeBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.PDF

    @override
    def _get_syntax(self) -> EnclosedSyntaxDefinition:
        return self._syntax_registry.get_pdf_syntax()

    @override
    def _get_file_data(self, block: Block) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.pdf
