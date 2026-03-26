from typing import override

from notionary.page.blocks.schemas import CreateFileBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.markdown.syntax.definition.models import SyntaxDefinition
from notionary.page.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


class FileParser(FileLikeBlockParser[CreateFileBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_file_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateFileBlock:
        return CreateFileBlock(file=file_data)
