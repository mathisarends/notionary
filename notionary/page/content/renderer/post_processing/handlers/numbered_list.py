import re
from typing import override

from notionary.page.content.renderer.post_processing.port import PostProcessor


class NumberedListPostProcessor(PostProcessor):
    """
    Handles post processing of numbered lists in markdown text.
    Would otherwise require complex state management during initial rendering.
    """

    NUMBERED_LIST_PLACEHOLDER = "__NUM__"
    LIST_ITEM_PATTERN = rf"^\s*{re.escape(NUMBERED_LIST_PLACEHOLDER)}\.\s+(.*)"
    NUMBERED_ITEM_PATTERN = r"^\d+\.\s+"

    @override
    def process(self, markdown_text: str) -> str:
        lines = markdown_text.splitlines()
        processed_lines = []
        list_counter = 1

        for line_index, line in enumerate(lines):
            if self._is_custom_list_item(line):
                content = self._extract_list_content(line)
                processed_lines.append(f"{list_counter}. {content}")
                list_counter += 1
            elif self._should_skip_blank_line(lines, line_index, processed_lines):
                continue
            else:
                list_counter = 1
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def _is_custom_list_item(self, line: str) -> bool:
        return bool(re.match(self.LIST_ITEM_PATTERN, line.strip()))

    def _extract_list_content(self, line: str) -> str:
        match = re.match(self.LIST_ITEM_PATTERN, line.strip())
        return match.group(1) if match else ""

    def _is_numbered_list_item(self, line: str) -> bool:
        return bool(re.match(self.NUMBERED_ITEM_PATTERN, line))

    def _is_blank_line(self, line: str) -> bool:
        return not line.strip()

    def _should_skip_blank_line(self, lines: list[str], current_index: int, processed_lines: list[str]) -> bool:
        if not self._is_blank_line(lines[current_index]):
            return False

        previous_is_list_item = processed_lines and self._is_numbered_list_item(processed_lines[-1])
        if not previous_is_list_item:
            return False

        next_index = current_index + 1
        if next_index >= len(lines):
            return False

        next_is_list_item = self._is_custom_list_item(lines[next_index])
        return next_is_list_item
