from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.mentions.port import MentionHandler
from notionary.rich_text.schemas import Mention
from notionary.shared.name_id_resolver.port import NameIdResolver


class DataSourceMentionHandler(MentionHandler):
    def __init__(
        self, markdown_grammar: MarkdownGrammar, data_source_resolver: NameIdResolver
    ):
        super().__init__(markdown_grammar)
        self._data_source_resolver = data_source_resolver

    async def handle(self, mention: Mention) -> str:
        if not mention.data_source:
            return ""

        data_source_name = await self._data_source_resolver.resolve_id_to_name(
            mention.data_source.id
        )
        return self._format_mention(
            self._markdown_grammar.datasource_mention_prefix,
            data_source_name or mention.data_source.id,
        )
