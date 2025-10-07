from typing import override

from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class ToggleMarkdownNode(MarkdownNode):
    def __init__(
        self, title: str, children: list[MarkdownNode] | None = None, syntax_registry: SyntaxRegistry | None = None
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.title = title
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        toggle_syntax = self._syntax_registry.get_toggle_syntax()
        result = f"{toggle_syntax.start_delimiter} {self.title}"

        if not self.children:
            result += f"\n{toggle_syntax.end_delimiter}"
            return result

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return result + "\n" + content_text + f"\n{toggle_syntax.end_delimiter}"
