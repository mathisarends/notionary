import re
from typing import override

from notionary.blocks.schemas import CodeData, CodingLanguage, CreateCodeBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser
from notionary.rich_text.markdown_to_rich_text.converter import (
    MarkdownRichTextConverter,
)
from notionary.rich_text.schemas import RichText


class CodeParser(LineParser):
    DEFAULT_LANGUAGE = CodingLanguage.PLAIN_TEXT

    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_converter: MarkdownRichTextConverter,
    ) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_code_syntax()
        self._rich_text_converter = rich_text_converter
        self._code_start_pattern = self._syntax.regex_pattern
        self._code_end_pattern = self._syntax.end_regex_pattern or re.compile(
            r"^```\s*$"
        )

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_code_fence_start(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        code_lines = self._collect_code_lines(context)
        lines_consumed = self._count_lines_consumed(context)

        block = await self._create_code_block(
            opening_line=context.line, code_lines=code_lines
        )
        if not block:
            return

        context.lines_consumed = lines_consumed
        context.result_blocks.append(block)

    def _is_code_fence_start(self, line: str) -> bool:
        return self._code_start_pattern.match(line) is not None

    def _is_code_fence_end(self, line: str) -> bool:
        return self._code_end_pattern.match(line) is not None

    def _collect_code_lines(self, context: BlockParsingContext) -> list[str]:
        code_lines = []
        for line in context.get_remaining_lines():
            if self._is_code_fence_end(line):
                break
            code_lines.append(line)
        return code_lines

    def _count_lines_consumed(self, context: BlockParsingContext) -> int:
        for line_index, line in enumerate(context.get_remaining_lines()):
            if self._is_code_fence_end(line):
                return line_index + 1
        return len(context.get_remaining_lines())

    async def _create_code_block(
        self, opening_line: str, code_lines: list[str]
    ) -> CreateCodeBlock | None:
        match = self._code_start_pattern.match(opening_line)
        if not match:
            return None

        language = self._parse_language(match.group(1))
        rich_text = await self._create_rich_text_from_code(code_lines)

        code_data = CodeData(rich_text=rich_text, language=language, caption=[])
        return CreateCodeBlock(code=code_data)

    def _parse_language(self, language_str: str | None) -> CodingLanguage:
        return CodingLanguage.from_string(language_str, default=self.DEFAULT_LANGUAGE)

    async def _create_rich_text_from_code(
        self, code_lines: list[str]
    ) -> list[RichText]:
        content = "\n".join(code_lines) if code_lines else ""
        return await self._rich_text_converter.to_rich_text(content)

    def _is_code_fence_start(self, line: str) -> bool:
        return self._code_start_pattern.match(line) is not None

    def _is_code_fence_end(self, line: str) -> bool:
        return self._code_end_pattern.match(line) is not None
