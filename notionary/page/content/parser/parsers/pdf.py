from typing import override

from notionary.blocks.schemas import CreatePdfBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.content.syntax.definition import SyntaxDefinition, SyntaxDefinitionRegistry


class PdfParser(FileLikeBlockParser[CreatePdfBlock]):
    @override
    def _get_syntax(self, syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
        return syntax_registry.get_pdf_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreatePdfBlock:
        return CreatePdfBlock(pdf=file_data)
