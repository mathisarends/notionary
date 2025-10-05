import re
from typing import override

from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BulletedListItemData, CreateBulletedListItemBlock
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class BulletedListParser(LineParser):
    PATTERN = re.compile(r"^(\s*)-\s+(?!\[[ x]\])(.+)$")

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.PATTERN.match(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_bulleted_list_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_bulleted_list_block(self, text: str) -> CreateBulletedListItemBlock | None:
        match = self.PATTERN.match(text)
        if not match:
            return None

        content = match.group(2)
        rich_text = await self._rich_text_converter.to_rich_text(content)

        bulleted_list_content = BulletedListItemData(rich_text=rich_text)
        return CreateBulletedListItemBlock(bulleted_list_item=bulleted_list_content)
