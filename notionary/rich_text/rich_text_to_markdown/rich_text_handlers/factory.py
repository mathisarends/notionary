from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers import (
    EquationHandler,
    TextHandler,
)
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers.mention import (
    MentionRichTextHandler,
    create_mention_handler_registry,
)
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.registry import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.schemas import RichTextType


def create_rich_text_handler_registry(
    markdown_grammar: MarkdownGrammar | None = None,
) -> RichTextHandlerRegistry:
    markdown_grammar = markdown_grammar or MarkdownGrammar()
    registry = RichTextHandlerRegistry()

    registry.register(
        RichTextType.TEXT,
        TextHandler(markdown_grammar),
    )

    registry.register(
        RichTextType.EQUATION,
        EquationHandler(markdown_grammar),
    )

    mention_registry = create_mention_handler_registry(markdown_grammar)

    registry.register(
        RichTextType.MENTION,
        MentionRichTextHandler(markdown_grammar, mention_registry),
    )

    return registry
