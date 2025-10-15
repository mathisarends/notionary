from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.page.content.markdown.nodes.base import MarkdownNode


class ChildrenRenderMixin:
    children: list[MarkdownNode]

    def render_children(self, indent_level: int = 1, indent_char: str = "    ") -> str:
        if not self.children:
            return ""

        rendered_parts = []
        indent = indent_char * indent_level

        for child in self.children:
            child_markdown = child.to_markdown()
            if child_markdown:
                indented = self.indent_text(child_markdown, indent)
                rendered_parts.append(indented)

        return "\n" + "\n".join(rendered_parts) if rendered_parts else ""

    def render_child(self, child: MarkdownNode, indent_level: int = 1, indent_char: str = "    ") -> str:
        child_markdown = child.to_markdown()
        if not child_markdown:
            return ""

        indent = indent_char * indent_level
        return self.indent_text(child_markdown, indent)

    @staticmethod
    def indent_text(text: str, indent: str = "    ") -> str:
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
