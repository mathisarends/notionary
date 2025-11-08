from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers import (
    EquationHandler,
    TextHandler,
    create_mention_rich_text_handler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handler import (
    MentionRichTextHandler,
)
from notionary.rich_text.rich_text_to_markdown.registry.service import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.schemas import RichTextType


def create_rich_text_handler_registry(
    mention_rich_text_handler: MentionRichTextHandler | None = None,
) -> RichTextHandlerRegistry:
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

    mention_rich_text_handler = (
        mention_rich_text_handler or create_mention_rich_text_handler()
    )

    registry.register(
        RichTextType.MENTION,
        mention_rich_text_handler,
    )

    return registry
