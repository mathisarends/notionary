from re import Match, Pattern

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import RichText


class StrikethroughPatternHandler(BasePatternHandler):
    def __init__(self, grammar: MarkdownGrammar) -> None:
        self._grammar = grammar

    @property
    def pattern(self) -> Pattern:
        return self._grammar.strikethrough_pattern

    async def handle(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), strikethrough=True)
