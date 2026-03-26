from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar
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
    MentionPatternHandler,
)
from notionary.rich_text.schemas import MentionType


def create_pattern_matcher() -> PatternMatcher:
    grammar = MarkdownGrammar()

    handlers: list[BasePatternHandler] = [
        UnderlinePatternHandler(grammar),
        BoldPatternHandler(grammar),
        ItalicPatternHandler(grammar, use_underscore=False),
        ItalicPatternHandler(grammar, use_underscore=True),
        StrikethroughPatternHandler(grammar),
        CodePatternHandler(grammar),
        LinkPatternHandler(grammar),
        EquationPatternHandler(grammar),
        MentionPatternHandler(MentionType.PAGE, grammar),
        MentionPatternHandler(MentionType.DATABASE, grammar),
        MentionPatternHandler(MentionType.DATASOURCE, grammar),
        MentionPatternHandler(MentionType.USER, grammar),
    ]

    return PatternMatcher(handlers)
