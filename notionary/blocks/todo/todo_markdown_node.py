from __future__ import annotations

from pydantic import Field
from notionary.markdown.markdown_node import MarkdownNode


class TodoMarkdownNode(MarkdownNode):
    """
    Enhanced Todo node with Pydantic integration.
    Programmatic interface for creating Markdown todo items (checkboxes).
    Supports checked and unchecked states.
    Example: - [ ] Task, - [x] Done
    """

    text: str
    checked: bool = False
    marker: str = Field(default="-")

    def to_markdown(self) -> str:
        # Validate marker in to_markdown to ensure it's valid
        valid_marker = self.marker if self.marker in {"-", "*", "+"} else "-"
        checkbox = "[x]" if self.checked else "[ ]"
        return f"{valid_marker} {checkbox} {self.text}"
