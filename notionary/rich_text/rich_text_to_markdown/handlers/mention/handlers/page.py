from typing import override

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handlers.base import (
    MentionHandler,
)
from notionary.rich_text.schemas import PageMention
from notionary.shared.name_id_resolver.port import NameIdResolver


class PageMentionHandler(MentionHandler):
    def __init__(
        self, markdown_grammar: MarkdownGrammar, page_resolver: NameIdResolver
    ):
        super().__init__(markdown_grammar)
        self._page_resolver = page_resolver

    @override
    async def handle(self, mention: PageMention) -> str:
        if not mention.page:
            return ""

        page_name = await self._page_resolver.resolve_id_to_name(mention.page.id)
        return self._format_mention(
            self._markdown_grammar.page_mention_prefix, page_name or mention.page.id
        )
