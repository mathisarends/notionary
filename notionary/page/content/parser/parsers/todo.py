from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateToDoBlock, CreateToDoData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax import SyntaxDefinitionRegistry


class TodoParser(LineParser):
    def __init__(
        self, syntax_registry: SyntaxDefinitionRegistry, rich_text_converter: MarkdownRichTextConverter
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_todo_syntax()
        self._syntax_done = syntax_registry.get_todo_done_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_todo_line(context.line)

    def _is_todo_line(self, line: str) -> bool:
        return (
            self._syntax.regex_pattern.match(line) is not None
            or self._syntax_done.regex_pattern.match(line) is not None
        )

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_todo_block(context.line)
        if not block:
            return

        await self._process_nested_children(block, context)
        context.result_blocks.append(block)

    async def _process_nested_children(self, block: CreateToDoBlock, context: BlockParsingContext) -> None:
        child_lines = self._collect_child_lines(context)
        if not child_lines:
            return

        child_blocks = await self._parse_child_blocks(child_lines, context)
        if child_blocks:
            block.to_do.children = child_blocks

        context.lines_consumed = len(child_lines)

    def _collect_child_lines(self, context: BlockParsingContext) -> list[str]:
        parent_indent_level = context.get_line_indentation_level()
        return context.collect_indented_child_lines(parent_indent_level)

    async def _parse_child_blocks(self, child_lines: list[str], context: BlockParsingContext) -> list[CreateToDoBlock]:
        stripped_lines = self._remove_parent_indentation(child_lines, context)
        children_text = self._convert_lines_to_text(stripped_lines)
        return await context.parse_nested_markdown(children_text)

    def _remove_parent_indentation(self, lines: list[str], context: BlockParsingContext) -> list[str]:
        return context.strip_indentation_level(lines, levels=1)

    def _convert_lines_to_text(self, lines: list[str]) -> str:
        return "\n".join(lines)

    async def _create_todo_block(self, text: str) -> CreateToDoBlock | None:
        content, checked = self._extract_todo_content(text)
        if content is None:
            return None

        rich_text = await self._convert_to_rich_text(content)
        return self._build_block(rich_text, checked)

    def _extract_todo_content(self, text: str) -> tuple[str | None, bool]:
        done_match = self._syntax_done.regex_pattern.match(text)
        if done_match:
            return done_match.group(1), True

        todo_match = self._syntax.regex_pattern.match(text)
        if todo_match:
            return todo_match.group(1), False

        return None, False

    async def _convert_to_rich_text(self, content: str):
        return await self._rich_text_converter.to_rich_text(content)

    def _build_block(self, rich_text, checked: bool) -> CreateToDoBlock:
        todo_content = CreateToDoData(
            rich_text=rich_text,
            checked=checked,
            color=BlockColor.DEFAULT,
        )
        return CreateToDoBlock(to_do=todo_content)
