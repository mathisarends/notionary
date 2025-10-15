from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins import ChildrenRenderMixin
from notionary.page.content.syntax.service import SyntaxRegistry


class QuoteMarkdownNode(ChildrenRenderMixin, MarkdownNode):
    def __init__(
        self,
        text: str,
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        quote_delimiter = self._get_quote_delimiter()
        result = f"{quote_delimiter} {self.text}"
        result += self.render_children()
        return result

    def _get_quote_delimiter(self) -> str:
        return self._syntax_registry.get_quote_syntax().start_delimiter
