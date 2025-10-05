import re
from typing import override

from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import CreateCalloutBlock, CreateCalloutData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.shared.models.icon_models import EmojiIcon


class CalloutParser(LineParser):
    CALLOUT_PATTERN = r'^\[callout\]\(([^"]+?)(?:\s+"([^"]+)")?\)$'
    DEFAULT_EMOJI = "💡"

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._pattern = re.compile(self.CALLOUT_PATTERN)
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_callout(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_callout_block(context.line)
        if block:
            context.result_blocks.append(block)

    def _is_callout(self, line: str) -> bool:
        return self._pattern.match(line.strip()) is not None

    async def _create_callout_block(self, line: str) -> CreateCalloutBlock | None:
        match = self._pattern.match(line.strip())
        if not match:
            return None

        content = match.group(1)
        emoji = match.group(2)

        if not content:
            return None

        if not emoji:
            emoji = self.DEFAULT_EMOJI

        rich_text = await self._rich_text_converter.to_rich_text(content.strip())
        callout_data = CreateCalloutData(
            rich_text=rich_text,
            icon=EmojiIcon(emoji=emoji),
        )

        return CreateCalloutBlock(callout=callout_data)
