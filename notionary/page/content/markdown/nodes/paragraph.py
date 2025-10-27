from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class ParagraphMarkdownNode(MarkdownNode):
    def __init__(
        self, text: str, syntax_registry: SyntaxDefinitionRegistry | None = None
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text

    @override
    def to_markdown(self) -> str:
        return self.text
