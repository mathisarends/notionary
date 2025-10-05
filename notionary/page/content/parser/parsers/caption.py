import re
from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class CaptionParser(LineParser):
    """
    Parser that handles caption lines and attaches them to the previous block.
    """

    CAPTION_PATTERN = re.compile(r"^\[caption\]\s+(.+)$")

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False

        if not self.CAPTION_PATTERN.match(context.line):
            return False

        if not context.result_blocks:
            return False

        previous_block = context.result_blocks[-1]
        return self._block_supports_caption(previous_block)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        caption_match = self.CAPTION_PATTERN.match(context.line)
        if not caption_match:
            return

        caption_text = caption_match.group(1)
        caption_rich_text = await self._rich_text_converter.to_rich_text(caption_text)

        previous_block = context.result_blocks[-1]
        self._attach_caption_to_block(previous_block, caption_rich_text)

    def _block_supports_caption(self, block: BlockCreatePayload) -> bool:
        block_data = getattr(block, block.type.value, None)
        if block_data is None:
            return False
        return hasattr(block_data, "caption")

    def _attach_caption_to_block(self, block: BlockCreatePayload, caption_rich_text: list) -> None:
        block_data = getattr(block, block.type.value)
        if hasattr(block_data, "caption"):
            block_data.caption = caption_rich_text
