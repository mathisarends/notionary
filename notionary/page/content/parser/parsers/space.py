from typing import override

from notionary.blocks.schemas import BlockColor, CreateParagraphBlock, ParagraphData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class SpaceParser(LineParser):
    """
    Parser for [space] markers that create empty paragraph blocks.
    Does not use SyntaxRegistry as it's just a simple string comparison.
    """

    SPACE_MARKER = "[space]"

    def __init__(self) -> None:
        super().__init__()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_space(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = self._create_space_block()
        if block:
            context.result_blocks.append(block)

    def _is_space(self, line: str) -> bool:
        return line.strip() == self.SPACE_MARKER

    def _create_space_block(self) -> CreateParagraphBlock:
        paragraph_data = ParagraphData(rich_text=[], color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_data)
