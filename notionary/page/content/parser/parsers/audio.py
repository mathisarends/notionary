from typing import override

from notionary.blocks.schemas import CreateAudioBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.content.syntax.definition import (
    SyntaxDefinition,
    SyntaxDefinitionRegistry,
)


class AudioParser(FileLikeBlockParser[CreateAudioBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_audio_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateAudioBlock:
        return CreateAudioBlock(audio=file_data)
