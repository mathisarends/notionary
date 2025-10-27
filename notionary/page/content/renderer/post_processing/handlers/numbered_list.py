import re
from enum import IntEnum
from typing import override

from notionary.page.content.renderer.post_processing.port import PostProcessor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar


class _NumberingStyle(IntEnum):
    NUMERIC = 0
    ALPHABETIC = 1
    ROMAN = 2


class _ListNumberingState:
    def __init__(self):
        self._counters_by_level: dict[int, int] = {}
        self._current_level = -1

    def advance_to_level(self, new_level: int) -> None:
        self._forget_deeper_levels_than(new_level)
        self._increment_counter_at_level(new_level)
        self._current_level = new_level

    def get_number_for_current_level(self) -> str:
        counter = self._counters_by_level[self._current_level]
        style = self._determine_numbering_style(self._current_level)
        return self._format_number(counter, style)

    def reset(self) -> None:
        self._counters_by_level.clear()
        self._current_level = -1

    def _forget_deeper_levels_than(self, level: int) -> None:
        self._counters_by_level = {
            existing_level: count
            for existing_level, count in self._counters_by_level.items()
            if existing_level <= level
        }

    def _increment_counter_at_level(self, level: int) -> None:
        self._counters_by_level[level] = self._counters_by_level.get(level, 0) + 1

    def _determine_numbering_style(self, nesting_level: int) -> _NumberingStyle:
        return _NumberingStyle(nesting_level % 3)

    def _format_number(self, counter: int, style: _NumberingStyle) -> str:
        if style == _NumberingStyle.NUMERIC:
            return str(counter)
        elif style == _NumberingStyle.ALPHABETIC:
            return self._to_alphabetic(counter)
        else:
            return self._to_roman(counter)

    def _to_alphabetic(self, number: int) -> str:
        result = ""
        number -= 1
        while number >= 0:
            result = chr(ord("a") + (number % 26)) + result
            number = number // 26 - 1
        return result

    def _to_roman(self, number: int) -> str:
        conversions = [
            (1000, "m"),
            (900, "cm"),
            (500, "d"),
            (400, "cd"),
            (100, "c"),
            (90, "xc"),
            (50, "l"),
            (40, "xl"),
            (10, "x"),
            (9, "ix"),
            (5, "v"),
            (4, "iv"),
            (1, "i"),
        ]

        result = ""
        for arabic, roman in conversions:
            while number >= arabic:
                result += roman
                number -= arabic
        return result


class NumberedListPlaceholderReplacerPostProcessor(PostProcessor):
    def __init__(self, markdown_grammar: MarkdownGrammar | None = None) -> None:
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()
        self._spaces_per_nesting_level = self._markdown_grammar.spaces_per_nesting_level
        self._numbered_list_placeholder = (
            self._markdown_grammar.numbered_list_placeholder
        )

    @override
    def process(self, markdown_text: str) -> str:
        lines = markdown_text.splitlines()
        return self._convert_placeholder_lists_to_numbered_lists(lines)

    def _convert_placeholder_lists_to_numbered_lists(self, lines: list[str]) -> str:
        result = []
        list_state = _ListNumberingState()

        for line_index, line in enumerate(lines):
            if self._is_placeholder_list_item(line):
                numbered_line = self._convert_to_numbered_item(line, list_state)
                result.append(numbered_line)
            elif self._is_blank_between_list_items(lines, line_index, result):
                continue
            else:
                list_state.reset()
                result.append(line)

        return "\n".join(result)

    def _convert_to_numbered_item(self, line: str, state: _ListNumberingState) -> str:
        indentation = self._extract_indentation(line)
        content = self._extract_content(line)
        nesting_level = self._calculate_nesting_level(indentation)

        state.advance_to_level(nesting_level)
        number = state.get_number_for_current_level()

        return f"{indentation}{number}. {content}"

    def _calculate_nesting_level(self, indentation: str) -> int:
        return len(indentation) // self._spaces_per_nesting_level

    def _extract_indentation(self, line: str) -> str:
        match = re.match(rf"^(\s*){re.escape(self._numbered_list_placeholder)}\.", line)
        return match.group(1) if match else ""

    def _extract_content(self, line: str) -> str:
        match = re.match(
            rf"^\s*{re.escape(self._numbered_list_placeholder)}\.\s*(.*)", line
        )
        return match.group(1) if match else ""

    def _is_placeholder_list_item(self, line: str) -> bool:
        return bool(
            re.match(rf"^\s*{re.escape(self._numbered_list_placeholder)}\.", line)
        )

    def _is_blank_between_list_items(
        self, lines: list[str], current_index: int, processed_lines: list[str]
    ) -> bool:
        if not self._is_blank(lines[current_index]):
            return False

        previous_line_was_list_item = (
            processed_lines and self._looks_like_numbered_list_item(processed_lines[-1])
        )
        if not previous_line_was_list_item:
            return False

        next_line_is_list_item = current_index + 1 < len(
            lines
        ) and self._is_placeholder_list_item(lines[current_index + 1])
        return next_line_is_list_item

    def _is_blank(self, line: str) -> bool:
        return not line.strip()

    def _looks_like_numbered_list_item(self, line: str) -> bool:
        return bool(re.match(r"^\s*(\d+|[a-z]+|[ivxlcdm]+)\.\s+", line))
