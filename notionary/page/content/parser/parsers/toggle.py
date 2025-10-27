from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateToggleBlock, CreateToggleData
from notionary.page.content.parser.parsers import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class ToggleParser(LineParser):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_converter: MarkdownRichTextConverter,
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_toggle_syntax()
        self._heading_syntax = syntax_registry.get_toggleable_heading_syntax()
        self._rich_text_converter = rich_text_converter

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_toggle_start(context)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_toggle_start(context):
            await self._process_toggle(context)

    def _is_toggle_start(self, context: BlockParsingContext) -> bool:
        if not self._syntax.regex_pattern.match(context.line):
            return False

        # Exclude toggleable heading patterns to be more resilient to wrong order of chain
        return not self.is_heading_start(context.line)

    def is_heading_start(self, line: str) -> bool:
        return self._heading_syntax.regex_pattern.match(line) is not None

    async def _process_toggle(self, context: BlockParsingContext) -> None:
        block = await self._create_toggle_block(context.line)
        if not block:
            return

        await self._process_nested_children(block, context)

        context.result_blocks.append(block)

    async def _create_toggle_block(self, line: str) -> CreateToggleBlock | None:
        if not (match := self._syntax.regex_pattern.match(line)):
            return None

        title = match.group(1).strip()
        rich_text = await self._rich_text_converter.to_rich_text(title)

        toggle_content = CreateToggleData(
            rich_text=rich_text, color=BlockColor.DEFAULT, children=[]
        )
        return CreateToggleBlock(toggle=toggle_content)

    async def _process_nested_children(
        self, block: CreateToggleBlock, context: BlockParsingContext
    ) -> None:
        parent_indent_level = context.get_line_indentation_level()
        child_lines = context.collect_indented_child_lines(parent_indent_level)

        if not child_lines:
            return

        stripped_lines = context.strip_indentation_level(child_lines, levels=1)
        child_markdown = "\n".join(stripped_lines)

        child_blocks = await context.parse_nested_markdown(child_markdown)
        block.toggle.children = child_blocks

        context.lines_consumed = len(child_lines)
