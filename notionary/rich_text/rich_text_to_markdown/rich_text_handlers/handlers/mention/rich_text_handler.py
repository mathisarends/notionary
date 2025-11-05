from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers.mention.registry import (
    MentionHandlerRegistry,
)
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.port import (
    RichTextHandler,
)
from notionary.rich_text.schemas import RichText


class MentionRichTextHandler(RichTextHandler):
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
            return ""

        return await handler.handle(mention)
