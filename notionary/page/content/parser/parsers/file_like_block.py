from abc import abstractmethod
from typing import Generic, TypeVar, override

from notionary.blocks.schemas import ExternalFileWithCaption
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser
from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.shared.models.file import ExternalFileData

_TBlock = TypeVar("_TBlock")


class FileLikeBlockParser(LineParser, Generic[_TBlock]):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = self._get_syntax(syntax_registry)

    @abstractmethod
    def _get_syntax(self, syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
        pass

    @abstractmethod
    def _create_block(self, file_data: ExternalFileWithCaption) -> _TBlock:
        pass

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        file_data = ExternalFileWithCaption(
            external=ExternalFileData(url=url),
        )
        block = self._create_block(file_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self._syntax.regex_pattern.search(line)
        return match.group(1).strip() if match else None
