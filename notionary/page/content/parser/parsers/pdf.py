from typing import override

from notionary.blocks.schemas import CreatePdfBlock, ExternalFileWithCaption
from notionary.markdown.syntax.definition import (
    SyntaxDefinition,
    SyntaxDefinitionRegistry,
)
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser


class PdfParser(FileLikeBlockParser[CreatePdfBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_pdf_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreatePdfBlock:
        return CreatePdfBlock(pdf=file_data)
