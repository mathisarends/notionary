from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.registry import (
    MentionHandlerRegistry,
)
from notionary.rich_text.rich_text_to_markdown.handlers.port import (
    RichTextHandler,
)
from notionary.rich_text.schemas import RichText
from notionary.utils.mixins.logging import LoggingMixin


class MentionRichTextHandler(RichTextHandler, LoggingMixin):
    def __init__(
        self,
        markdown_grammar: MarkdownGrammar,
        mention_handler_registry: MentionHandlerRegistry,
    ):
        super().__init__(markdown_grammar)
        self._mention_handler_registry = mention_handler_registry

    async def handle(self, rich_text: RichText) -> str:
        if not rich_text.mention:
            return ""

        mention = rich_text.mention
        handler = self._mention_handler_registry.get_handler(mention.type)

        if not handler:
            self.logger.warning(
                f"No handler found for mention type: {mention.type}. Skipping."
            )
            return ""

        return await handler.handle(mention)
