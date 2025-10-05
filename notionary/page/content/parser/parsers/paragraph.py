from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateParagraphBlock, ParagraphData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class ParagraphParser(LineParser):
    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return bool(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_paragraph_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_paragraph_block(self, text: str) -> CreateParagraphBlock | None:
        if not text:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(text)
        paragraph_content = ParagraphData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)
