from typing import override

from notionary.blocks.schemas import (
    CreateBulletedListItemBlock,
    CreateBulletedListItemData,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_to_rich_text.service import (
    MarkdownRichTextConverter,
)


class BulletedListParser(LineParser):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_converter: MarkdownRichTextConverter,
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_bulleted_list_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_bulleted_list_line(context.line)

    def _is_bulleted_list_line(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_bulleted_list_block(context.line)
        if not block:
            return

        await self._process_nested_children(block, context)
        context.result_blocks.append(block)

    async def _process_nested_children(
        self, block: CreateBulletedListItemBlock, context: BlockParsingContext
    ) -> None:
        child_lines = self._collect_child_lines(context)
        if not child_lines:
            return

        child_blocks = await self._parse_child_blocks(child_lines, context)
        if child_blocks:
            block.bulleted_list_item.children = child_blocks

        context.lines_consumed = len(child_lines)

    def _collect_child_lines(self, context: BlockParsingContext) -> list[str]:
        parent_indent_level = context.get_line_indentation_level()
        return context.collect_indented_child_lines(parent_indent_level)

    async def _parse_child_blocks(
        self, child_lines: list[str], context: BlockParsingContext
    ) -> list[CreateBulletedListItemBlock]:
        stripped_lines = self._remove_parent_indentation(child_lines, context)
        children_text = self._convert_lines_to_text(stripped_lines)
        return await context.parse_nested_markdown(children_text)

    def _remove_parent_indentation(
        self, lines: list[str], context: BlockParsingContext
    ) -> list[str]:
        return context.strip_indentation_level(lines, levels=1)

    def _convert_lines_to_text(self, lines: list[str]) -> str:
        return "\n".join(lines)

    async def _create_bulleted_list_block(
        self, text: str
    ) -> CreateBulletedListItemBlock | None:
        content = self._extract_list_content(text)
        if content is None:
            return None

        rich_text = await self._convert_to_rich_text(content)
        return self._build_block(rich_text)

    def _extract_list_content(self, text: str) -> str | None:
        match = self._syntax.regex_pattern.match(text)
        if not match:
            return None
        return match.group(2)

    async def _convert_to_rich_text(self, content: str):
        return await self._rich_text_converter.to_rich_text(content)

    def _build_block(self, rich_text) -> CreateBulletedListItemBlock:
        bulleted_list_content = CreateBulletedListItemData(rich_text=rich_text)
        return CreateBulletedListItemBlock(bulleted_list_item=bulleted_list_content)
