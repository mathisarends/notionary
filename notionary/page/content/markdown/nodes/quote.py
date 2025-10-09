from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class QuoteMarkdownNode(MarkdownNode):
    def __init__(self, text: str, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.text = text

    @override
    def to_markdown(self) -> str:
        quote_syntax = self._syntax_registry.get_quote_syntax()
        return f"{quote_syntax.start_delimiter} {self.text}"
