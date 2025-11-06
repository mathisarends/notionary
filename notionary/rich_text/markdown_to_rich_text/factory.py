from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.converter import (
    MarkdownRichTextConverter,
)
from notionary.rich_text.markdown_to_rich_text.handlers.factory import (
    create_pattern_matcher,
)


def create_markdown_to_rich_text_converter() -> MarkdownRichTextConverter:
    pattern_matcher = create_pattern_matcher()
    markdown_grammar = MarkdownGrammar()

    return MarkdownRichTextConverter(
        pattern_matcher=pattern_matcher,
        grammar=markdown_grammar,
    )
