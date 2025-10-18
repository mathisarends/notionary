from typing import override

from notionary.blocks.enums import BlockColor
from notionary.blocks.schemas import CreateParagraphBlock, CreateParagraphData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax import SyntaxRegistry


class SpaceParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_space_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False

        if self._is_explicit_space_marker(context):
            return True

        return self._is_second_consecutive_empty_line(context)

    def _is_explicit_space_marker(self, context: BlockParsingContext) -> bool:
        return self._syntax.regex_pattern.match(context.line.strip()) is not None

    def _is_second_consecutive_empty_line(self, context: BlockParsingContext) -> bool:
        return context.line.strip() == "" and context.is_previous_line_empty

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = self._create_space_block()
        if block:
            context.result_blocks.append(block)

    def _create_space_block(self) -> CreateParagraphBlock:
        paragraph_data = CreateParagraphData(rich_text=[], color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_data)
