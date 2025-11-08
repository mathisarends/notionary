from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handler import (
    MentionRichTextHandler,
)
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


def create_mention_rich_text_handler(
    markdown_grammar: MarkdownGrammar | None = None,
    page_resolver: PageNameIdResolver | None = None,
    database_resolver: DatabaseNameIdResolver | None = None,
    data_source_resolver: DataSourceNameIdResolver | None = None,
    person_resolver: PersonNameIdResolver | None = None,
) -> MentionRichTextHandler:
    markdown_grammar = markdown_grammar or MarkdownGrammar()
    mention_handler_registry = _create_mention_handler_registry(
        markdown_grammar,
        page_resolver,
        database_resolver,
        data_source_resolver,
        person_resolver,
    )
    return MentionRichTextHandler(
        markdown_grammar=markdown_grammar,
        mention_handler_registry=mention_handler_registry,
    )


def _create_mention_handler_registry(
    markdown_grammar: MarkdownGrammar,
    page_resolver: PageNameIdResolver | None = None,
    database_resolver: DatabaseNameIdResolver | None = None,
    data_source_resolver: DataSourceNameIdResolver | None = None,
    person_resolver: PersonNameIdResolver | None = None,
) -> MentionHandlerRegistry:
    page_resolver = page_resolver or PageNameIdResolver()
    database_resolver = database_resolver or DatabaseNameIdResolver()
    data_source_resolver = data_source_resolver or DataSourceNameIdResolver()
    person_resolver = person_resolver or PersonNameIdResolver()

    registry = MentionHandlerRegistry()

    registry.register(
        MentionType.PAGE,
        PageMentionHandler(markdown_grammar, page_resolver),
    )
    registry.register(
        MentionType.DATABASE,
        DatabaseMentionHandler(markdown_grammar, database_resolver),
    )
    registry.register(
        MentionType.DATASOURCE,
        DataSourceMentionHandler(markdown_grammar, data_source_resolver),
    )
    registry.register(
        MentionType.USER,
        UserMentionHandler(markdown_grammar, person_resolver),
    )
    registry.register(
        MentionType.DATE,
        DateMentionHandler(markdown_grammar),
    )

    return registry
