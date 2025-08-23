from __future__ import annotations

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode


class EquationMarkdownBlockParams(BaseModel):
    expression: str


class EquationMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown equation blocks.
    Uses standard Markdown equation syntax with double dollar signs.
    
    Examples:
    $$E = mc^2$$
    $$\\frac{a}{b} + \\sqrt{c}$$
    $$\\int_0^\\infty e^{-x} dx = 1$$
    """

    def __init__(self, expression: str):
        self.expression = expression

    @classmethod
    def from_params(cls, params: EquationMarkdownBlockParams) -> EquationMarkdownNode:
        return cls(expression=params.expression)

    def to_markdown(self) -> str:
        expr = self.expression.strip()
        if not expr:
            return "$$$$"

        return f"$${expr}$$"
