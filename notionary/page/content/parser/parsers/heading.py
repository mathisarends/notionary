import re
from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    BlockColor,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateHeadingBlock,
    CreateHeadingData,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class HeadingParser(LineParser):
    HEADING_PATTERN = r"^(#{1,3})[ \t]+(.+)$"

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._pattern = re.compile(self.HEADING_PATTERN)
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_heading(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_heading_block(context.line)
        if block:
            context.result_blocks.append(block)

    def _is_heading(self, line: str) -> bool:
        return self._pattern.match(line) is not None

    async def _create_heading_block(self, line: str) -> CreateHeadingBlock | None:
        match = self._pattern.match(line)
        if not match:
            return None

        level = len(match.group(1))
        if level < 1 or level > 3:
            return None

        content = match.group(2).strip()
        if not content:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(content)
        heading_data = CreateHeadingData(rich_text=rich_text, color=BlockColor.DEFAULT, is_toggleable=False)

        if level == 1:
            return CreateHeading1Block(heading_1=heading_data)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_data)
        else:
            return CreateHeading3Block(heading_3=heading_data)
