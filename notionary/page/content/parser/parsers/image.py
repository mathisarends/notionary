from typing import override

from notionary.blocks.schemas import CreateImageBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.content.syntax.definition import (
    SyntaxDefinition,
    SyntaxDefinitionRegistry,
)


class ImageParser(FileLikeBlockParser[CreateImageBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_image_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateImageBlock:
        return CreateImageBlock(image=file_data)
