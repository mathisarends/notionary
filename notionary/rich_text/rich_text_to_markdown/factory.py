from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.rich_text_to_markdown.registry import (
    RichTextHandlerRegistry,
    create_rich_text_handler_registry,
)


def create_rich_text_to_markdown_converter(
    markdown_grammar: MarkdownGrammar | None = None,
    rich_text_handler_registry: RichTextHandlerRegistry | None = None,
) -> RichTextToMarkdownConverter:
    markdown_grammar = markdown_grammar or MarkdownGrammar()
    rich_text_handler_registry = (
        rich_text_handler_registry or create_rich_text_handler_registry()
    )
    return RichTextToMarkdownConverter(markdown_grammar, rich_text_handler_registry)
