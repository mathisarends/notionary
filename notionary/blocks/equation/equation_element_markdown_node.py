from __future__ import annotations

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode


class EquationMarkdownBlockParams(BaseModel):
    expression: str


class EquationMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown equation blocks.
    Example:
    [equation](E = mc^2)
    [equation]("f(x) = \\sin(x) + \\cos(x)")
    """

    def __init__(self, expression: str):
        self.expression = expression

    @classmethod
    def from_params(cls, params: EquationMarkdownBlockParams) -> EquationMarkdownNode:
        return cls(expression=params.expression)

    def to_markdown(self) -> str:
        expr = self.expression.strip()
        if not expr:
            return "[equation]()"

        if ("\n" in expr) or (")" in expr) or ('"' in expr):
            escaped = expr.replace("\\", "\\\\").replace('"', r"\"")
            return f'[equation]("{escaped}")'

        return f"[equation]({expr})"
