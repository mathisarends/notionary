from notionary.rich_text.rich_text_to_markdown.handlers import (
    EquationHandler,
    MentionRichTextHandler,
    TextHandler,
)
from notionary.rich_text.rich_text_to_markdown.registry.service import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.schemas import RichTextType


def create_rich_text_handler_registry() -> RichTextHandlerRegistry:
    registry = RichTextHandlerRegistry()

    registry.register(
        RichTextType.TEXT,
        TextHandler(),
    )

    registry.register(
        RichTextType.EQUATION,
        EquationHandler(),
    )

    registry.register(
        RichTextType.MENTION,
        MentionRichTextHandler(),
    )

    return registry
