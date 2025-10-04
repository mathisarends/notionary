import re
from typing import override

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import CodeData, CodeLanguage, CreateCodeBlock
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class CodeParser(LineParser):
    CODE_FENCE = "```"
    CODE_START_PATTERN = r"^```(\w*)\s*(?:\"([^\"]*)\")?\s*$"
    CODE_END_PATTERN = r"^```\s*$"
    DEFAULT_LANGUAGE = CodeLanguage.PLAIN_TEXT

    def __init__(self) -> None:
        super().__init__()
        self._code_start_pattern = re.compile(self.CODE_START_PATTERN)
        self._code_end_pattern = re.compile(self.CODE_END_PATTERN)

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_code_fence_start(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        code_lines = self._collect_code_lines(context)
        lines_consumed = self._count_lines_consumed(context)

        block = self._create_code_block(opening_line=context.line, code_lines=code_lines)

        if block:
            context.lines_consumed = lines_consumed
            context.result_blocks.append(block)

    def _is_code_fence_start(self, line: str) -> bool:
        return self._code_start_pattern.match(line.strip()) is not None

    def _is_code_fence_end(self, line: str) -> bool:
        return self._code_end_pattern.match(line.strip()) is not None

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

    def _create_code_block(self, opening_line: str, code_lines: list[str]) -> CreateCodeBlock | None:
        match = self._code_start_pattern.match(opening_line.strip())
        if not match:
            return None

        language = self._parse_language(match.group(1))
        caption = self._parse_caption(match.group(2))
        rich_text = self._create_rich_text_from_code(code_lines)

        code_data = CodeData(rich_text=rich_text, language=language, caption=caption)
        return CreateCodeBlock(code=code_data)

    def _parse_language(self, language_str: str | None) -> CodeLanguage:
        if not language_str:
            return self.DEFAULT_LANGUAGE

        normalized_language = language_str.lower()

        for language_enum in CodeLanguage:
            if language_enum.value.lower() == normalized_language:
                return language_enum

        return self.DEFAULT_LANGUAGE

    def _parse_caption(self, caption_str: str | None) -> list[RichText]:
        if not caption_str:
            return []
        return [RichText.for_caption(caption_str)]

    def _create_rich_text_from_code(self, code_lines: list[str]) -> list[RichText]:
        if not code_lines:
            return []

        content = "\n".join(code_lines)
        return [RichText.for_code_block(content)]
