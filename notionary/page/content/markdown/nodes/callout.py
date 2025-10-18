from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins import ChildrenRenderMixin
from notionary.page.content.syntax import SyntaxRegistry


class CalloutMarkdownNode(ChildrenRenderMixin, MarkdownNode):
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
        callout_content = self._format_callout_content()
        start_delimiter = self._syntax_registry.get_callout_syntax().start_delimiter
        result = f"{start_delimiter}({callout_content})"

        result += self.render_children()

        return result

    def _format_callout_content(self) -> str:
        if self.emoji:
            return f'{self.text} "{self.emoji}"'
        return self.text
