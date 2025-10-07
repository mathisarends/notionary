from typing import override

from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class HeadingMarkdownNode(MarkdownNode):
    def __init__(self, text: str, level: int = 1, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.level = max(1, min(3, level))

    @override
    def to_markdown(self) -> str:
        heading_syntax = self._syntax_registry.get_heading_syntax()
        return f"{heading_syntax.start_delimiter * self.level} {self.text}"
