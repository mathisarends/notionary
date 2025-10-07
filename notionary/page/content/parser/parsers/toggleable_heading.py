from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    BlockColor,
    BlockCreatePayload,
    BlockType,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateHeadingBlock,
    CreateHeadingData,
)
from notionary.page.content.parser.parsers import (
    BlockParsingContext,
    LineParser,
    ParentBlockContext,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class ToggleableHeadingParser(LineParser):
    MIN_HEADING_LEVEL = 1
    MAX_HEADING_LEVEL = 3

    HEADING_BLOCK_TYPES = (CreateHeading1Block, CreateHeading2Block, CreateHeading3Block)

    def __init__(self, syntax_registry: SyntaxRegistry, rich_text_converter: MarkdownRichTextConverter) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_toggleable_heading_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_heading_start(context) or self._is_heading_end(context) or self._is_heading_content(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_heading_start(context):
            await self._start_toggleable_heading(context)
        elif self._is_heading_end(context):
            await self._finalize_toggleable_heading(context)
        elif self._is_heading_content(context):
            await self._add_heading_content(context)

    def _is_heading_start(self, context: BlockParsingContext) -> bool:
        return self._syntax.regex_pattern.match(context.line) is not None

    def _is_heading_end(self, context: BlockParsingContext) -> bool:
        if not self._syntax.end_regex_pattern.match(context.line):
            return False
        return self._has_heading_on_stack(context)

    def _is_heading_content(self, context: BlockParsingContext) -> bool:
        if not self._has_heading_on_stack(context):
            return False

        return not (
            self._syntax.regex_pattern.match(context.line) or self._syntax.end_regex_pattern.match(context.line)
        )

    def _has_heading_on_stack(self, context: BlockParsingContext) -> bool:
        if not context.parent_stack:
            return False
        current_parent = context.parent_stack[-1]
        return isinstance(current_parent.block, self.HEADING_BLOCK_TYPES)

    async def _start_toggleable_heading(self, context: BlockParsingContext) -> None:
        block = await self._create_heading_block(context.line)
        if not block:
            return

        parent_context = ParentBlockContext(
            block=block,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _create_heading_block(self, line: str) -> CreateHeadingBlock | None:
        match = self._syntax.regex_pattern.match(line)
        if not match:
            return None

        level = len(match.group("level"))
        content = match.group(2).strip()

        if not self._is_valid_heading(level, content):
            return None

        heading_data = await self._build_heading_data(content)

        if level == 1:
            return CreateHeading1Block(heading_1=heading_data)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_data)
        else:
            return CreateHeading3Block(heading_3=heading_data)

    def _is_valid_heading(self, level: int, content: str) -> bool:
        return self.MIN_HEADING_LEVEL <= level <= self.MAX_HEADING_LEVEL and bool(content)

    async def _build_heading_data(self, content: str) -> CreateHeadingData:
        rich_text = await self._rich_text_converter.to_rich_text(content)
        return CreateHeadingData(rich_text=rich_text, color=BlockColor.DEFAULT, is_toggleable=True, children=[])

    async def _add_heading_content(self, context: BlockParsingContext) -> None:
        context.parent_stack[-1].add_child_line(context.line)

    async def _finalize_toggleable_heading(self, context: BlockParsingContext) -> None:
        heading_context = context.parent_stack.pop()
        await self._assign_children(heading_context, context)
        self._add_to_parent_or_result(heading_context.block, context)

    async def _assign_children(self, heading_context: ParentBlockContext, context: BlockParsingContext) -> None:
        children = await self._collect_children(heading_context, context)
        self._set_heading_children(heading_context.block, children)

    async def _collect_children(
        self, heading_context: ParentBlockContext, context: BlockParsingContext
    ) -> list[BlockCreatePayload]:
        children = []

        if heading_context.child_lines:
            text = "\n".join(heading_context.child_lines)
            text_blocks = await self._parse_nested_content(text, context)
            children.extend(text_blocks)

        if heading_context.child_blocks:
            children.extend(heading_context.child_blocks)

        return children

    def _set_heading_children(self, block: CreateHeadingBlock, children: list[BlockCreatePayload]) -> None:
        if block.type == BlockType.HEADING_1:
            block.heading_1.children = children
        elif block.type == BlockType.HEADING_2:
            block.heading_2.children = children
        elif block.type == BlockType.HEADING_3:
            block.heading_3.children = children

    def _add_to_parent_or_result(self, block: CreateHeadingBlock, context: BlockParsingContext) -> None:
        if context.parent_stack:
            context.parent_stack[-1].add_child_block(block)
        else:
            context.result_blocks.append(block)

    async def _parse_nested_content(self, text: str, context: BlockParsingContext) -> list:
        if not text.strip():
            return []
        return await context.parse_nested_content(text)
