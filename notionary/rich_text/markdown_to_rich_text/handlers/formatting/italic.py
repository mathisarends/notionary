from re import Match, Pattern

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import RichText


class ItalicPatternHandler(BasePatternHandler):
    def __init__(self, grammar: MarkdownGrammar, use_underscore: bool = False) -> None:
        self._grammar = grammar
        self._use_underscore = use_underscore

    @property
    def pattern(self) -> Pattern:
        if self._use_underscore:
            return self._grammar.italic_underscore_pattern
        return self._grammar.italic_pattern

    async def handle(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), italic=True)
