from re import Pattern

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.mention.base import (
    MentionPatternHandler,
)
from notionary.rich_text.schemas import MentionType, RichText


class DatabaseMentionPatternHandler(MentionPatternHandler):
    def __init__(self, grammar: MarkdownGrammar) -> None:
        self._grammar = grammar

    @property
    def pattern(self) -> Pattern:
        return self._grammar.database_mention_pattern

    @property
    def mention_type(self) -> MentionType:
        return MentionType.DATABASE

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_database(resolved_id)
