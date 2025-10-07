from typing import override

from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class CalloutMarkdownNode(MarkdownNode):
    def __init__(
        self,
        text: str,
        emoji: str | None = None,
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.emoji = emoji
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        callout_syntax = self._syntax_registry.get_callout_syntax()
        start_tag = f"{callout_syntax.start_delimiter} {self.emoji}" if self.emoji else callout_syntax.start_delimiter

        if not self.children:
            return f"{start_tag}\n{self.text}\n{callout_syntax.end_delimiter}"

        # Convert children to markdown
        content_parts = [self.text] + [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return f"{start_tag}\n{content_text}\n{callout_syntax.end_delimiter}"
