from typing import override

from notionary.page.markdown.nodes.base import MarkdownNode
from notionary.page.markdown.syntax.definition import SyntaxDefinitionRegistry


class DividerMarkdownNode(MarkdownNode):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def to_markdown(self) -> str:
        divider_syntax = self._syntax_registry.get_divider_syntax()
        return divider_syntax.start_delimiter
