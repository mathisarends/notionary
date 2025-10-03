from notionary.blocks.markdown.nodes.base import MarkdownNode


class EquationMarkdownNode(MarkdownNode):
    """
    Enhanced Equation node with Pydantic integration.
    Programmatic interface for creating Markdown equation blocks.
    Uses standard Markdown equation syntax with double dollar signs.

    Examples:
    $$E = mc^2$$
    $$\\frac{a}{b} + \\sqrt{c}$$
    $$\\int_0^\\infty e^{-x} dx = 1$$
    """

    expression: str

    def to_markdown(self) -> str:
        expr = self.expression.strip()
        if not expr:
            return "$$$$"

        return f"$${expr}$$"
