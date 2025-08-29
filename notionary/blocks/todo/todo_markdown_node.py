from __future__ import annotations
from notionary.markdown.markdown_node import MarkdownNode

class TodoMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown todo items (checkboxes).
    Supports checked and unchecked states.
    Example: - [ ] Task, - [x] Done
    """

    def __init__(self, text: str, checked: bool = False, marker: str = "-"):
        self.text = text
        self.checked = checked
        self.marker = marker if marker in {"-", "*", "+"} else "-"

    def to_markdown(self) -> str:
        checkbox = "[x]" if self.checked else "[ ]"
        return f"{self.marker} {checkbox} {self.text}"
