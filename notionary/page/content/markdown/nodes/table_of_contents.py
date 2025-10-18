from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


class TableOfContentsMarkdownNode(MarkdownNode):
    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def to_markdown(self) -> str:
        toc_syntax = self._syntax_registry.get_table_of_contents_syntax()
        return toc_syntax.start_delimiter
