from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class TodoMarkdownNode(MarkdownNode):
    def __init__(
        self, text: str, checked: bool = False, marker: str = "-", syntax_registry: SyntaxRegistry | None = None
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.checked = checked
        self.marker = marker

    @override
    def to_markdown(self) -> str:
        # Validate marker to ensure it's valid
        valid_marker = self.marker if self.marker in {"-", "*", "+"} else "-"
        todo_syntax = self._syntax_registry.get_todo_syntax()
        checkbox_state = todo_syntax.end_delimiter if self.checked else todo_syntax.start_delimiter
        return f"{valid_marker} {checkbox_state} {self.text}"
