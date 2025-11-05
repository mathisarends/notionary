from typing import override

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers.mention.handlers.base import (
    MentionHandler,
)
from notionary.rich_text.schemas import Mention
from notionary.shared.name_id_resolver.port import NameIdResolver


class DatabaseMentionHandler(MentionHandler):
    def __init__(
        self, markdown_grammar: MarkdownGrammar, database_resolver: NameIdResolver
    ):
        super().__init__(markdown_grammar)
        self._database_resolver = database_resolver

    @override
    async def handle(self, mention: Mention) -> str:
        if not mention.database:
            return ""

        database_name = await self._database_resolver.resolve_id_to_name(
            mention.database.id
        )
        return self._format_mention(
            self._markdown_grammar.database_mention_prefix,
            database_name or mention.database.id,
        )
