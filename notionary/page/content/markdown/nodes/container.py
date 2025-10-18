from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.grammar import MarkdownGrammar


class ContainerNode(MarkdownNode):
    children: list[MarkdownNode]

    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        grammar = self._syntax_registry._markdown_grammar if self._syntax_registry else MarkdownGrammar()
        self._spaces_per_nesting_level = grammar.spaces_per_nesting_level

    def render_children(self, indent_level: int = 1) -> str:
        if not self.children:
            return ""

        rendered_parts = []
        indent = " " * (self._spaces_per_nesting_level * indent_level)

        for child in self.children:
            child_markdown = child.to_markdown()
            if child_markdown:
                indented = self.indent_text(child_markdown, indent)
                rendered_parts.append(indented)

        return "\n" + "\n".join(rendered_parts) if rendered_parts else ""

    def render_child(self, child: MarkdownNode, indent_level: int = 1) -> str:
        child_markdown = child.to_markdown()
        if not child_markdown:
            return ""

        indent = " " * (self._spaces_per_nesting_level * indent_level)
        return self.indent_text(child_markdown, indent)

    @staticmethod
    def indent_text(text: str, indent: str) -> str:
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
