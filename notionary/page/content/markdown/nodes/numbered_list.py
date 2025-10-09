from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class NumberedListMarkdownNode(MarkdownNode):
    def __init__(self, texts: list[str], syntax_registry: SyntaxRegistry | None = None):
        super().__init__(syntax_registry=syntax_registry)
        self.texts = texts

    @override
    def to_markdown(self) -> str:
        numbered_list_syntax = self._syntax_registry.get_numbered_list_syntax()
        return "\n".join(f"{i + 1}{numbered_list_syntax.end_delimiter} {text}" for i, text in enumerate(self.texts))
