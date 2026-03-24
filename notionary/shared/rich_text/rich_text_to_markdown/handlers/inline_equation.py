from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.port import (
    RichTextHandler,
)
from notionary.rich_text.schemas import RichText


class EquationHandler(RichTextHandler):
    def __init__(self, markdown_grammar: MarkdownGrammar):
        super().__init__(markdown_grammar)

    async def handle(self, rich_text: RichText) -> str:
        if not rich_text.equation:
            return ""

        return (
            f"{self._markdown_grammar.inline_equation_wrapper}"
            f"{rich_text.equation.expression}"
            f"{self._markdown_grammar.inline_equation_wrapper}"
        )
