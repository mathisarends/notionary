import re
from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import CreateCalloutBlock, CreateCalloutData
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry
from notionary.shared.models.icon_models import EmojiIcon


class CalloutParser(LineParser):
    CALLOUT_END_PATTERN = r"^:::\s*$"
    DEFAULT_EMOJI = "💡"

    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_callout_syntax()
        self._start_pattern = self._syntax.regex_pattern
        self._end_pattern = re.compile(self.CALLOUT_END_PATTERN)
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_callout_start(context) or self._is_callout_end(context) or self._is_callout_content(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_callout_start(context):
            await self._start_callout(context)

        if self._is_callout_end(context):
            await self._finalize_callout(context)

        if self._is_callout_content(context):
            self._add_callout_content(context)

    def _is_callout_start(self, context: BlockParsingContext) -> bool:
        return self._start_pattern.match(context.line) is not None

    def _is_callout_end(self, context: BlockParsingContext) -> bool:
        if not self._end_pattern.match(context.line):
            return False

        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return isinstance(current_parent.block, CreateCalloutBlock)

    async def _start_callout(self, context: BlockParsingContext) -> None:
        block = await self._create_callout_block(context.line)
        if not block:
            return

        parent_context = ParentBlockContext(
            block=block,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _create_callout_block(self, line: str) -> CreateCalloutBlock | None:
        match = self._start_pattern.match(line)
        if not match:
            return None

        emoji_part = match.group(1)
        emoji = emoji_part.strip() if emoji_part else self.DEFAULT_EMOJI

        # Create callout with empty rich_text initially
        # The actual content will be added as children
        callout_data = CreateCalloutData(
            rich_text=[],
            icon=EmojiIcon(emoji=emoji),
            children=[],
        )
        return CreateCalloutBlock(callout=callout_data)

    async def _finalize_callout(self, context: BlockParsingContext) -> None:
        callout_context = context.parent_stack.pop()
        await self._assign_callout_children_if_any(callout_context, context)

        if self._is_nested_in_other_parent_context(context):
            self._assign_to_parent_context(context, callout_context)
        else:
            context.result_blocks.append(callout_context.block)

    def _is_nested_in_other_parent_context(self, context: BlockParsingContext) -> bool:
        return bool(context.parent_stack)

    def _assign_to_parent_context(self, context: BlockParsingContext, callout_context: ParentBlockContext) -> None:
        parent_context = context.parent_stack[-1]
        parent_context.add_child_block(callout_context.block)

    async def _assign_callout_children_if_any(
        self, callout_context: ParentBlockContext, context: BlockParsingContext
    ) -> None:
        all_children = []

        if callout_context.child_lines:
            children_text = "\n".join(callout_context.child_lines)
            text_blocks = await self._parse_nested_content(children_text, context)
            all_children.extend(text_blocks)

        # Add any child blocks
        if callout_context.child_blocks:
            all_children.extend(callout_context.child_blocks)

        callout_context.block.callout.children = all_children

    def _is_callout_content(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not isinstance(current_parent.block, CreateCalloutBlock):
            return False

        return not (self._start_pattern.match(context.line) or self._end_pattern.match(context.line))

    def _add_callout_content(self, context: BlockParsingContext) -> None:
        context.parent_stack[-1].add_child_line(context.line)

    async def _parse_nested_content(self, text: str, context: BlockParsingContext) -> list:
        if not text.strip():
            return []

        return await context.parse_nested_content(text)
