from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.markdown_to_rich_text.handlers.equation import (
    EquationPatternHandler,
)
from notionary.rich_text.markdown_to_rich_text.handlers.formatting import (
    BoldPatternHandler,
    CodePatternHandler,
    ItalicPatternHandler,
    LinkPatternHandler,
    StrikethroughPatternHandler,
    UnderlinePatternHandler,
)
from notionary.rich_text.markdown_to_rich_text.handlers.matcher import (
    PatternMatcher,
)
from notionary.rich_text.markdown_to_rich_text.handlers.mention import (
    DatabaseMentionPatternHandler,
    DataSourceMentionPatternHandler,
    PageMentionPatternHandler,
    UserMentionPatternHandler,
)
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


def create_pattern_matcher(
    page_resolver: PageNameIdResolver | None = None,
    database_resolver: DatabaseNameIdResolver | None = None,
    data_source_resolver: DataSourceNameIdResolver | None = None,
    person_resolver: PersonNameIdResolver | None = None,
) -> PatternMatcher:
    grammar = MarkdownGrammar()
    page_resolver = page_resolver or PageNameIdResolver()
    database_resolver = database_resolver or DatabaseNameIdResolver()
    data_source_resolver = data_source_resolver or DataSourceNameIdResolver()
    person_resolver = person_resolver or PersonNameIdResolver()

    handlers: list[BasePatternHandler] = [
        UnderlinePatternHandler(grammar),
        BoldPatternHandler(grammar),
        ItalicPatternHandler(grammar, use_underscore=False),
        ItalicPatternHandler(grammar, use_underscore=True),
        StrikethroughPatternHandler(grammar),
        CodePatternHandler(grammar),
        LinkPatternHandler(grammar),
        EquationPatternHandler(grammar),
        PageMentionPatternHandler(page_resolver, grammar),
        DatabaseMentionPatternHandler(database_resolver, grammar),
        DataSourceMentionPatternHandler(data_source_resolver, grammar),
        UserMentionPatternHandler(person_resolver, grammar),
    ]

    return PatternMatcher(handlers)
