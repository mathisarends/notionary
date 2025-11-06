from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.rich_text_to_markdown.handlers.factory import (
    create_rich_text_handler_registry,
)


def create_rich_text_to_markdown_converter() -> RichTextToMarkdownConverter:
    markdown_grammar = MarkdownGrammar()
    rich_text_handler_registry = create_rich_text_handler_registry()

    return RichTextToMarkdownConverter(
        markdown_grammar=markdown_grammar,
        rich_text_handler_registry=rich_text_handler_registry,
    )
