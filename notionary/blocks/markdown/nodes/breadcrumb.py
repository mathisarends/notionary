from typing import override

from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class BreadcrumbMarkdownNode(MarkdownNode):
    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def to_markdown(self) -> str:
        breadcrumb_syntax = self._syntax_registry.get_breadcrumb_syntax()
        return breadcrumb_syntax.start_delimiter
