from typing import override

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.mention.port import MentionHandler
from notionary.rich_text.schemas import Mention
from notionary.shared.name_id_resolver.port import NameIdResolver


class UserMentionHandler(MentionHandler):
    def __init__(
        self, markdown_grammar: MarkdownGrammar, person_resolver: NameIdResolver
    ):
        super().__init__(markdown_grammar)
        self._person_resolver = person_resolver

    @override
    async def handle(self, mention: Mention) -> str:
        if not mention.user:
            return ""

        user_name = await self._person_resolver.resolve_id_to_name(mention.user.id)
        return self._format_mention(
            self._markdown_grammar.user_mention_prefix, user_name or mention.user.id
        )
