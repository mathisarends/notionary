from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.container import ContainerNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class TodoMarkdownNode(ContainerNode):
    VALID_MARKER = "-"

    def __init__(
        self,
        text: str,
        checked: bool = False,
        marker: str = "-",
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.checked = checked
        self.marker = marker
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        validated_marker = self._get_validated_marker()
        checkbox_state = self._get_checkbox_state()
        result = f"{validated_marker}{checkbox_state} {self.text}"
        result += self.render_children()
        return result

    def _get_validated_marker(self) -> str:
        return self.marker if self.marker == self.VALID_MARKER else self.VALID_MARKER

    def _get_checkbox_state(self) -> str:
        todo_syntax = self._syntax_registry.get_todo_syntax()
        return todo_syntax.end_delimiter if self.checked else todo_syntax.start_delimiter
