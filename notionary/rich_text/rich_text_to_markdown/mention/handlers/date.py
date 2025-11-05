from typing import override

from notionary.rich_text.rich_text_to_markdown.mention.port import MentionHandler
from notionary.rich_text.schemas import Mention, MentionDate


class DateMentionHandler(MentionHandler):
    @override
    async def handle(self, mention: Mention) -> str:
        if not mention.date:
            return ""

        date_range = self._format_date_range(mention.date)
        return self._format_mention(
            self._markdown_grammar.date_mention_prefix, date_range
        )

    def _format_date_range(self, date_mention: MentionDate) -> str:
        if date_mention.end:
            return f"{date_mention.start}–{date_mention.end}"

        return date_mention.start
