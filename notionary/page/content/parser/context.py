from __future__ import annotations

from collections.abc import Awaitable, Callable

from notionary.blocks.schemas import BlockCreatePayload
from notionary.markdown import MarkdownGrammar


class ParentBlockContext:
    def __init__(
        self,
        block: BlockCreatePayload,
        child_lines: list[str],
        child_blocks: list[BlockCreatePayload] | None = None,
    ) -> None:
        self.block = block
        self.child_lines = child_lines
        self.child_blocks = child_blocks if child_blocks is not None else []

    def add_child_line(self, content: str) -> None:
        self.child_lines.append(content)

    def add_child_block(self, block: BlockCreatePayload) -> None:
        self.child_blocks.append(block)


_ParseChildrenCallback = Callable[[str], Awaitable[list[BlockCreatePayload]]]


class BlockParsingContext:
    def __init__(
        self,
        line: str,
        result_blocks: list[BlockCreatePayload],
        parent_stack: list[ParentBlockContext],
        parse_children_callback: _ParseChildrenCallback | None = None,
        all_lines: list[str] | None = None,
        current_line_index: int | None = None,
        lines_consumed: int = 0,
        is_previous_line_empty: bool = False,
        markdown_grammar: MarkdownGrammar | None = None,
    ) -> None:
        self.line = line
        self.result_blocks = result_blocks
        self.parent_stack = parent_stack
        self.parse_children_callback = parse_children_callback
        self.all_lines = all_lines
        self.current_line_index = current_line_index
        self.lines_consumed = lines_consumed
        self.is_previous_line_empty = is_previous_line_empty
        markdown_grammar = markdown_grammar or MarkdownGrammar()
        self._spaces_per_nesting_level = markdown_grammar.spaces_per_nesting_level

    async def parse_nested_markdown(self, text: str) -> list[BlockCreatePayload]:
        if not self._can_parse_children(text):
            return []

        return await self.parse_children_callback(text)

    def _can_parse_children(self, text: str) -> bool:
        return self.parse_children_callback is not None and bool(text)

    def get_remaining_lines(self) -> list[str]:
        if not self._has_remaining_lines():
            return []
        return self.all_lines[self.current_line_index + 1 :]

    def _has_remaining_lines(self) -> bool:
        return self.all_lines is not None and self.current_line_index is not None

    def is_inside_parent_context(self) -> bool:
        return len(self.parent_stack) > 0

    def get_line_indentation_level(self, line: str | None = None) -> int:
        target_line = self._get_target_line(line)
        leading_spaces = self._count_leading_spaces(target_line)
        return self._calculate_indentation_level(leading_spaces)

    def _get_target_line(self, line: str | None) -> str:
        return line if line is not None else self.line

    def _count_leading_spaces(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _calculate_indentation_level(self, leading_spaces: int) -> int:
        return leading_spaces // self._spaces_per_nesting_level

    def collect_indented_child_lines(self, parent_indent_level: int) -> list[str]:
        child_lines = []
        expected_child_indent = parent_indent_level + 1

        for line in self.get_remaining_lines():
            if self._should_include_line_as_child(line, expected_child_indent):
                child_lines.append(line)
            else:
                break

        return child_lines

    def _should_include_line_as_child(self, line: str, expected_indent: int) -> bool:
        if self._is_empty_line(line):
            return True

        line_indent = self.get_line_indentation_level(line)
        return line_indent >= expected_indent

    def _is_empty_line(self, line: str) -> bool:
        return not line.strip()

    def strip_indentation_level(self, lines: list[str], levels: int = 1) -> list[str]:
        return [self._strip_line_indentation(line, levels) for line in lines]

    def _strip_line_indentation(self, line: str, levels: int) -> str:
        if self._is_empty_line(line):
            return line

        spaces_to_remove = self._calculate_spaces_to_remove(levels)
        return self._remove_leading_spaces(line, spaces_to_remove)

    def _calculate_spaces_to_remove(self, levels: int) -> int:
        return self._spaces_per_nesting_level * levels

    def _remove_leading_spaces(self, line: str, spaces: int) -> str:
        if len(line) < spaces:
            return line
        return line[spaces:]
