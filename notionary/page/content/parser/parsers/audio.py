from typing import override

from notionary.blocks.schemas import CreateAudioBlock, ExternalFileWithCaption
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser
from notionary.page.content.syntax import SyntaxDefinition, SyntaxRegistry


class AudioParser(FileLikeBlockParser[CreateAudioBlock]):
    @override
    def _get_syntax(self, syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
        return syntax_registry.get_audio_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateAudioBlock:
        return CreateAudioBlock(audio=file_data)
