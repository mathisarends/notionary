from typing import override

from notionary.blocks.schemas import CreateImageBlock, ExternalFileWithCaption
from notionary.markdown.syntax.definition import (
    SyntaxDefinition,
    SyntaxDefinitionRegistry,
)
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser


class ImageParser(FileLikeBlockParser[CreateImageBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_image_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateImageBlock:
        return CreateImageBlock(image=file_data)
