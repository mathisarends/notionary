from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import CreateCalloutBlock, CreateCalloutData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry
from notionary.shared.models.icon import EmojiIcon


class CalloutParser(LineParser):
    DEFAULT_EMOJI = "💡"

    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_callout_syntax()
        self._pattern = self._syntax.regex_pattern
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._pattern.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        match = self._pattern.search(context.line)
        if not match:
            return

        content = match.group(1).strip()
        emoji = match.group(2) if match.lastindex >= 2 and match.group(2) else self.DEFAULT_EMOJI

        # Convert content to rich text
        rich_text = await self._rich_text_converter.to_rich_text(content)

        callout_data = CreateCalloutData(
            rich_text=rich_text,
            icon=EmojiIcon(emoji=emoji),
            children=[],
        )
        block = CreateCalloutBlock(callout=callout_data)

        if self._is_nested_in_parent_context(context):
            context.parent_stack[-1].add_child_block(block)
        else:
            context.result_blocks.append(block)

    def _is_nested_in_parent_context(self, context: BlockParsingContext) -> bool:
        return bool(context.parent_stack)
