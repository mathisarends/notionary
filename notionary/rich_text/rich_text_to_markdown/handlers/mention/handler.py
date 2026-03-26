import logging

from notionary.rich_text.rich_text_to_markdown.handlers.port import RichTextHandler
from notionary.rich_text.schemas import (
    DatabaseMention,
    DataSourceMention,
    DateMention,
    MentionDate,
    MentionType,
    PageMention,
    RichText,
    UserMention,
)

logger = logging.getLogger(__name__)


class MentionRichTextHandler(RichTextHandler):
    def handle(self, rich_text: RichText) -> str:
        if not rich_text.mention:
            return ""

        mention = rich_text.mention

        match mention.type:
            case MentionType.PAGE:
                return self._handle_page(mention)
            case MentionType.DATABASE:
                return self._handle_database(mention)
            case MentionType.DATASOURCE:
                return self._handle_data_source(mention)
            case MentionType.USER:
                return self._handle_user(mention)
            case MentionType.DATE:
                return self._handle_date(mention)
            case _:
                logger.warning(f"Unhandled mention type: {mention.type}")
                return ""

    def _handle_page(self, mention: PageMention) -> str:
        if not mention.page:
            return ""
        return self._format_mention(
            self._markdown_grammar.page_mention_prefix, mention.page.id
        )

    def _handle_database(self, mention: DatabaseMention) -> str:
        if not mention.database:
            return ""
        return self._format_mention(
            self._markdown_grammar.database_mention_prefix, mention.database.id
        )

    def _handle_data_source(self, mention: DataSourceMention) -> str:
        if not mention.data_source:
            return ""
        return self._format_mention(
            self._markdown_grammar.datasource_mention_prefix, mention.data_source.id
        )

    def _handle_user(self, mention: UserMention) -> str:
        if not mention.user:
            return ""
        return self._format_mention(
            self._markdown_grammar.user_mention_prefix, mention.user.id
        )

    def _handle_date(self, mention: DateMention) -> str:
        if not mention.date:
            return ""
        date_str = self._format_date_range(mention.date)
        return self._format_mention(
            self._markdown_grammar.date_mention_prefix, date_str
        )

    def _format_mention(self, prefix: str, value: str) -> str:
        return f"{prefix}{value}{self._markdown_grammar.mention_suffix}"

    def _format_date_range(self, date: MentionDate) -> str:
        if date.end:
            return f"{date.start}\u2013{date.end}"
        return date.start
