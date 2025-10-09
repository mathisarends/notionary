from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class BulletedListMarkdownNode(MarkdownNode):
    def __init__(self, texts: list[str], syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.texts = texts

    @override
    def to_markdown(self) -> str:
        bulleted_list_syntax = self._syntax_registry.get_bulleted_list_syntax()
        result = []
        for text in self.texts:
            result.append(f"{bulleted_list_syntax.start_delimiter} {text}")
        return "\n".join(result)
