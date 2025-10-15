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
        block = await self._create_callout_block(context.line)
        if not block:
            return

        await self._process_nested_children(block, context)

        if self._is_nested_in_parent_context(context):
            context.parent_stack[-1].add_child_block(block)
        else:
            context.result_blocks.append(block)

    async def _process_nested_children(self, block: CreateCalloutBlock, context: BlockParsingContext) -> None:
        child_lines = self._collect_child_lines(context)
        if not child_lines:
            return

        child_blocks = await self._parse_child_blocks(child_lines, context)
        if child_blocks:
            block.callout.children = child_blocks

        context.lines_consumed = len(child_lines)

    def _collect_child_lines(self, context: BlockParsingContext) -> list[str]:
        parent_indent_level = context.get_line_indentation_level()
        return context.collect_indented_child_lines(parent_indent_level)

    async def _parse_child_blocks(
        self, child_lines: list[str], context: BlockParsingContext
    ) -> list[CreateCalloutBlock]:
        stripped_lines = self._remove_parent_indentation(child_lines, context)
        children_text = self._convert_lines_to_text(stripped_lines)
        return await context.parse_nested_markdown(children_text)

    def _remove_parent_indentation(self, lines: list[str], context: BlockParsingContext) -> list[str]:
        return context.strip_indentation_level(lines, levels=1)

    def _convert_lines_to_text(self, lines: list[str]) -> str:
        return "\n".join(lines)

    async def _create_callout_block(self, line: str) -> CreateCalloutBlock | None:
        match = self._pattern.search(line)
        if not match:
            return None

        content = match.group(1).strip()
        emoji = self._extract_emoji(match)

        rich_text = await self._convert_to_rich_text(content)
        return self._build_block(rich_text, emoji)

    def _extract_emoji(self, match) -> str:
        if match.lastindex >= 2 and match.group(2):
            return match.group(2)
        return self.DEFAULT_EMOJI

    async def _convert_to_rich_text(self, content: str):
        return await self._rich_text_converter.to_rich_text(content)

    def _build_block(self, rich_text, emoji: str) -> CreateCalloutBlock:
        callout_data = CreateCalloutData(
            rich_text=rich_text,
            icon=EmojiIcon(emoji=emoji),
            children=[],
        )
        return CreateCalloutBlock(callout=callout_data)

    def _is_nested_in_parent_context(self, context: BlockParsingContext) -> bool:
        return bool(context.parent_stack)
