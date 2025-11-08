from re import Match, Pattern

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import RichText


class EquationPatternHandler(BasePatternHandler):
    def __init__(self, grammar: MarkdownGrammar) -> None:
        self._grammar = grammar

    @property
    def pattern(self) -> Pattern:
        return self._grammar.inline_equation_pattern

    async def handle(self, match: Match) -> RichText:
        expression = match.group(1)
        return RichText.equation_inline(expression)
