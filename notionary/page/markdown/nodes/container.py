from notionary.markdown.nodes.base import MarkdownNode
from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


def flatten_children(children: list[MarkdownNode]) -> MarkdownNode | None:
    """Convert a list of child nodes to a single node for container compatibility."""
    if not children:
        return None
    if len(children) == 1:
        return children[0]
    return _MultiChildWrapper(children)


class _MultiChildWrapper(MarkdownNode):
    def __init__(self, children: list[MarkdownNode]) -> None:
        super().__init__()
        self.children = children

    def to_markdown(self) -> str:
        return "\n".join(child.to_markdown() for child in self.children if child)


class ContainerNode(MarkdownNode):
    children: list[MarkdownNode]

    def __init__(self, syntax_registry: SyntaxDefinitionRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)
        grammar = self._get_grammar(syntax_registry)
        self._spaces_per_nesting_level = grammar.spaces_per_nesting_level

    def render_children(self, indent_level: int = 1) -> str:
        if not self.children:
            return ""

        indent = self._calculate_indent(indent_level)
        rendered = [self._indent_child(child, indent) for child in self.children]
        rendered = [text for text in rendered if text]

        return f"\n{'\n'.join(rendered)}" if rendered else ""

    def render_child(self, child: MarkdownNode, indent_level: int = 1) -> str:
        child_markdown = child.to_markdown()
        if not child_markdown:
            return ""

        indent = self._calculate_indent(indent_level)
        return self._indent_text(child_markdown, indent)

    def _calculate_indent(self, level: int) -> str:
        return " " * (self._spaces_per_nesting_level * level)

    def _indent_child(self, child: MarkdownNode, indent: str) -> str:
        child_markdown = child.to_markdown()
        return self._indent_text(child_markdown, indent) if child_markdown else ""

    @staticmethod
    def _indent_text(text: str, indent: str) -> str:
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)

    @staticmethod
    def _get_grammar(
        syntax_registry: SyntaxDefinitionRegistry | None,
    ) -> MarkdownGrammar:
        return (
            syntax_registry._markdown_grammar if syntax_registry else MarkdownGrammar()
        )
