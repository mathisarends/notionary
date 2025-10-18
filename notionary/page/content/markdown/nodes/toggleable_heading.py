from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


class ToggleableHeadingMarkdownNode(MarkdownNode):
    def __init__(
        self,
        text: str,
        level: int,
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.level = max(1, min(3, level))
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        toggle_syntax = self._syntax_registry.get_toggle_syntax()
        heading_syntax = self._syntax_registry.get_heading_syntax()
        prefix = toggle_syntax.start_delimiter + (heading_syntax.start_delimiter * self.level)
        result = f"{prefix} {self.text}"

        if not self.children:
            result += f"\n{toggle_syntax.end_delimiter}"
            return result

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return result + "\n" + content_text + f"\n{toggle_syntax.end_delimiter}"
