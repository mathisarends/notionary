from typing import override

from notionary.blocks.schemas import CreateVideoBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.content.syntax import SyntaxDefinition, SyntaxDefinitionRegistry


class VideoParser(FileLikeBlockParser[CreateVideoBlock]):
    @override
    def _get_syntax(self, syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
        return syntax_registry.get_video_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateVideoBlock:
        return CreateVideoBlock(video=file_data)
