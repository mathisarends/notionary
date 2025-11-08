from re import Pattern

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.mention.base import (
    MentionPatternHandler,
)
from notionary.rich_text.schemas import MentionType, RichText
from notionary.shared.name_id_resolver import NameIdResolver


class UserMentionPatternHandler(MentionPatternHandler):
    def __init__(self, resolver: NameIdResolver, grammar: MarkdownGrammar) -> None:
        super().__init__(resolver)
        self._grammar = grammar

    @property
    def pattern(self) -> Pattern:
        return self._grammar.user_mention_pattern

    @property
    def mention_type(self) -> MentionType:
        return MentionType.USER

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_user(resolved_id)
