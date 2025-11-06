from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.markdown_to_rich_text.handlers.color import (
    ColorPatternHandler,
)
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
from notionary.rich_text.markdown_to_rich_text.handlers.mention import (
    DatabaseMentionPatternHandler,
    DataSourceMentionPatternHandler,
    PageMentionPatternHandler,
    UserMentionPatternHandler,
)
from notionary.rich_text.markdown_to_rich_text.handlers.registry import (
    PatternHandlerRegistry,
)
from notionary.shared.name_id_resolver import NameIdResolver

if TYPE_CHECKING:
    from notionary.rich_text.markdown_to_rich_text.converter import (
        MarkdownRichTextConverter,
    )


def create_pattern_handler_registry(
    *,
    page_resolver: NameIdResolver,
    database_resolver: NameIdResolver,
    data_source_resolver: NameIdResolver,
    person_resolver: NameIdResolver,
    grammar: MarkdownGrammar,
    converter: MarkdownRichTextConverter,
) -> PatternHandlerRegistry:
    handlers: list[BasePatternHandler] = [
        BoldPatternHandler(grammar),
        ItalicPatternHandler(grammar, use_underscore=False),
        ItalicPatternHandler(grammar, use_underscore=True),
        UnderlinePatternHandler(grammar),
        StrikethroughPatternHandler(grammar),
        CodePatternHandler(grammar),
        LinkPatternHandler(grammar),
        EquationPatternHandler(grammar),
        ColorPatternHandler(grammar, converter),
        PageMentionPatternHandler(page_resolver, grammar),
        DatabaseMentionPatternHandler(database_resolver, grammar),
        DataSourceMentionPatternHandler(data_source_resolver, grammar),
        UserMentionPatternHandler(person_resolver, grammar),
    ]

    return PatternHandlerRegistry(handlers)
