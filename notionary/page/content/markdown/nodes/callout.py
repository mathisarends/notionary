from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class CalloutMarkdownNode(MarkdownNode):
    def __init__(
        self,
        text: str,
        emoji: str | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.emoji = emoji

    @override
    def to_markdown(self) -> str:
        syntax = self._syntax_registry.get_callout_syntax()

        # Build callout using syntax service delimiters
        if self.emoji:
            return f'{syntax.start_delimiter}{self.text} "{self.emoji}"{syntax.end_delimiter}'
        else:
            return f"{syntax.start_delimiter}{self.text}{syntax.end_delimiter}"
