from typing import override

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
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_to_rich_text.service import (
    MarkdownRichTextConverter,
)


class HeadingParser(LineParser):
    MIN_HEADING_LEVEL = 1
    MAX_HEADING_LEVEL = 3

    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_converter: MarkdownRichTextConverter,
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_heading_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.match(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_heading_block(context.line)
        if not block:
            return

        await self._process_nested_children(block, context)
        context.result_blocks.append(block)

    async def _process_nested_children(
        self, block: CreateHeadingBlock, context: BlockParsingContext
    ) -> None:
        parent_indent_level = context.get_line_indentation_level()
        child_lines = context.collect_indented_child_lines(parent_indent_level)

        if not child_lines:
            return

        child_lines = self._remove_trailing_empty_lines(child_lines)

        if not child_lines:
            return

        self._set_heading_toggleable(block, True)

        stripped_lines = context.strip_indentation_level(child_lines, levels=1)
        child_markdown = "\n".join(stripped_lines)

        child_blocks = await context.parse_nested_markdown(child_markdown)
        self._set_heading_children(block, child_blocks)

        context.lines_consumed = len(child_lines)

    def _set_heading_toggleable(
        self, block: CreateHeadingBlock, is_toggleable: bool
    ) -> None:
        if block.type == BlockType.HEADING_1:
            block.heading_1.is_toggleable = is_toggleable
        elif block.type == BlockType.HEADING_2:
            block.heading_2.is_toggleable = is_toggleable
        elif block.type == BlockType.HEADING_3:
            block.heading_3.is_toggleable = is_toggleable

    def _set_heading_children(
        self, block: CreateHeadingBlock, children: list[BlockCreatePayload]
    ) -> None:
        if block.type == BlockType.HEADING_1:
            block.heading_1.children = children
        elif block.type == BlockType.HEADING_2:
            block.heading_2.children = children
        elif block.type == BlockType.HEADING_3:
            block.heading_3.children = children

    def _remove_trailing_empty_lines(self, lines: list[str]) -> list[str]:
        while lines and not lines[-1].strip():
            lines.pop()
        return lines

    async def _create_heading_block(self, line: str) -> CreateHeadingBlock | None:
        match = self._syntax.regex_pattern.match(line)
        if not match:
            return None

        level = len(match.group(1))
        content = match.group(2).strip()

        if not self._is_valid_heading(level, content):
            return None

        heading_data = await self._build_heading_data(content)
        return self._create_heading_block_by_level(level, heading_data)

    def _is_valid_heading(self, level: int, content: str) -> bool:
        return self.MIN_HEADING_LEVEL <= level <= self.MAX_HEADING_LEVEL and bool(
            content
        )

    async def _build_heading_data(self, content: str) -> CreateHeadingData:
        rich_text = await self._rich_text_converter.to_rich_text(content)
        return CreateHeadingData(
            rich_text=rich_text,
            color=BlockColor.DEFAULT,
            is_toggleable=False,
            children=[],
        )

    def _create_heading_block_by_level(
        self, level: int, heading_data: CreateHeadingData
    ) -> CreateHeadingBlock:
        if level == 1:
            return CreateHeading1Block(heading_1=heading_data)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_data)
        else:
            return CreateHeading3Block(heading_3=heading_data)
