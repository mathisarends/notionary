from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


class DividerMarkdownNode(MarkdownNode):
    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def to_markdown(self) -> str:
        divider_syntax = self._syntax_registry.get_divider_syntax()
        return divider_syntax.start_delimiter
