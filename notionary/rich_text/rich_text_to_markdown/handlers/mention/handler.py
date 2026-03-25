import logging

from notionary.shared.rich_text.rich_text_to_markdown.handlers.port import (
    RichTextHandler,
)
from notionary.shared.rich_text.schemas import (
    DatabaseMention,
    DateMention,
    MentionDate,
    MentionType,
    PageMention,
    RichText,
    UserMention,
)

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar

logger = logging.getLogger(__name__)


class MentionRichTextHandler(RichTextHandler):
    def __init__(self, markdown_grammar: MarkdownGrammar) -> None:
        super().__init__(markdown_grammar)

    async def handle(self, rich_text: RichText) -> str:
        if not rich_text.mention:
            return ""

        mention = rich_text.mention

        match mention.type:
            case MentionType.PAGE:
                return await self._handle_page(mention)
            case MentionType.DATABASE:
                return await self._handle_database(mention)
            case MentionType.USER:
                return await self._handle_user(mention)
            case MentionType.DATE:
                return self._handle_date(mention)
            case _:
                logger.warning(f"Unhandled mention type: {mention.type}")
                return ""

    async def _handle_page(self, mention: PageMention) -> str:
        if not mention.page:
            return ""
        name = await self._resolve_page_name(mention.page.id)
        return self._format_mention(
            self._markdown_grammar.page_mention_prefix, name or mention.page.id
        )

    async def _handle_database(self, mention: DatabaseMention) -> str:
        if not mention.database:
            return ""
        name = await self._resolve_database_name(mention.database.id)
        return self._format_mention(
            self._markdown_grammar.database_mention_prefix,
            name or mention.database.id,
        )

    async def _handle_user(self, mention: UserMention) -> str:
        if not mention.user:
            return ""
        name = await self._resolve_user_name(mention.user.id)
        return self._format_mention(
            self._markdown_grammar.user_mention_prefix, name or mention.user.id
        )

    def _handle_date(self, mention: DateMention) -> str:
        if not mention.date:
            return ""
        date_str = self._format_date_range(mention.date)
        return self._format_mention(
            self._markdown_grammar.date_mention_prefix, date_str
        )

    def _format_mention(self, prefix: str, name: str) -> str:
        return f"{prefix}{name}{self._markdown_grammar.mention_suffix}"

    def _format_date_range(self, date: MentionDate) -> str:
        if date.end:
            return f"{date.start}\u2013{date.end}"
        return date.start

    async def _resolve_page_name(self, page_id: str) -> str | None:
        try:
            from notionary import Page

            page = await Page.from_id(page_id)
            return page.title if page else None
        except Exception:
            return None

    async def _resolve_database_name(self, database_id: str) -> str | None:
        try:
            from notionary import Database

            database = await Database.from_id(database_id)
            return database.title if database else None
        except Exception:
            return None

    async def _resolve_user_name(self, user_id: str) -> str | None:
        try:
            from notionary.http.client import HttpClient
            from notionary.user.client import UserClient

            client = UserClient(HttpClient())
            user = await client.get(user_id)
            return user.name if user else None
        except Exception:
            return None
