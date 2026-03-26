from collections.abc import Callable
from re import Match, Pattern
from typing import ClassVar

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import MentionType, RichText


class MentionPatternHandler(BasePatternHandler):
    _MENTION_CONFIGS: ClassVar[
        dict[MentionType, tuple[str, Callable[[str], RichText]]]
    ] = {
        MentionType.PAGE: ("page_mention_pattern", RichText.mention_page),
        MentionType.DATABASE: ("database_mention_pattern", RichText.mention_database),
        MentionType.DATASOURCE: (
            "datasource_mention_pattern",
            RichText.mention_data_source,
        ),
        MentionType.USER: ("user_mention_pattern", RichText.mention_user),
    }

    def __init__(self, mention_type: MentionType, grammar: MarkdownGrammar) -> None:
        config = self._MENTION_CONFIGS[mention_type]
        self._pattern: Pattern = getattr(grammar, config[0])
        self._create_mention = config[1]

    @property
    def pattern(self) -> Pattern:
        return self._pattern

    async def handle(self, match: Match) -> RichText:
        identifier = match.group(1)
        return self._create_mention(identifier)
