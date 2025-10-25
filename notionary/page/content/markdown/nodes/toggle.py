from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.container import ContainerNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


class ToggleMarkdownNode(ContainerNode):
    def __init__(
        self,
        title: str,
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.title = title
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        toggle_delimiter = self._get_toggle_delimiter()
        result = f"{toggle_delimiter} {self.title}"
        result += self.render_children()
        return result

    def _get_toggle_delimiter(self) -> str:
        return self._syntax_registry.get_toggle_syntax().start_delimiter
