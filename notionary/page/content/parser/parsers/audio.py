from typing import override

from notionary.blocks.schemas import CreateAudioBlock, ExternalFileWithCaption
from notionary.markdown.syntax.definition.models import SyntaxDefinition
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.file_like_block import FileLikeBlockParser


class AudioParser(FileLikeBlockParser[CreateAudioBlock]):
    @override
    def _get_syntax(
        self, syntax_registry: SyntaxDefinitionRegistry
    ) -> SyntaxDefinition:
        return syntax_registry.get_audio_syntax()

    @override
    def _create_block(self, file_data: ExternalFileWithCaption) -> CreateAudioBlock:
        return CreateAudioBlock(audio=file_data)
