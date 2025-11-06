from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handlers import (
    DatabaseMentionHandler,
    DataSourceMentionHandler,
    DateMentionHandler,
    PageMentionHandler,
    UserMentionHandler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.mention.registry import (
    MentionHandlerRegistry,
)
from notionary.rich_text.schemas import MentionType
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


def create_mention_handler_registry(
    markdown_grammar: MarkdownGrammar | None = None,
) -> MentionHandlerRegistry:
    grammar = markdown_grammar or MarkdownGrammar()
    page_resolver = PageNameIdResolver()
    database_resolver = DatabaseNameIdResolver()
    data_source_resolver = DataSourceNameIdResolver()
    person_resolver = PersonNameIdResolver()

    registry = MentionHandlerRegistry()

    registry.register(
        MentionType.PAGE,
        PageMentionHandler(grammar, page_resolver),
    )
    registry.register(
        MentionType.DATABASE,
        DatabaseMentionHandler(grammar, database_resolver),
    )
    registry.register(
        MentionType.DATASOURCE,
        DataSourceMentionHandler(grammar, data_source_resolver),
    )
    registry.register(
        MentionType.USER,
        UserMentionHandler(grammar, person_resolver),
    )
    registry.register(
        MentionType.DATE,
        DateMentionHandler(grammar),
    )

    return registry
