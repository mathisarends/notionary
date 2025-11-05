from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.mention.handlers import (
    DatabaseMentionHandler,
    DataSourceMentionHandler,
    DateMentionHandler,
    PageMentionHandler,
    UserMentionHandler,
)
from notionary.rich_text.rich_text_to_markdown.mention.registry import (
    MentionHandlerRegistry,
)
from notionary.rich_text.schemas import MentionType
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


class MentionHandlerRegistryFactory:
    def __init__(self, markdown_grammar: MarkdownGrammar | None = None) -> None:
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()

    def create(self) -> MentionHandlerRegistry:
        page_resolver = PageNameIdResolver()
        database_resolver = DatabaseNameIdResolver()
        data_source_resolver = DataSourceNameIdResolver()
        person_resolver = PersonNameIdResolver()

        registry = MentionHandlerRegistry()

        registry.register(
            MentionType.PAGE,
            PageMentionHandler(self._markdown_grammar, page_resolver),
        )
        registry.register(
            MentionType.DATABASE,
            DatabaseMentionHandler(self._markdown_grammar, database_resolver),
        )
        registry.register(
            MentionType.DATASOURCE,
            DataSourceMentionHandler(self._markdown_grammar, data_source_resolver),
        )
        registry.register(
            MentionType.USER,
            UserMentionHandler(self._markdown_grammar, person_resolver),
        )
        registry.register(
            MentionType.DATE,
            DateMentionHandler(self._markdown_grammar),
        )

        return registry
