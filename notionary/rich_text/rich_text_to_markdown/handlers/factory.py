from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.inline_equation import (
    EquationHandler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.mention.factory import (
    create_mention_handler_registry,
)
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handler import (
    MentionRichTextHandler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.registry import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.rich_text_to_markdown.handlers.text import TextHandler
from notionary.rich_text.schemas import RichTextType


def create_rich_text_handler_registry() -> RichTextHandlerRegistry:
    markdown_grammar = MarkdownGrammar()
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
