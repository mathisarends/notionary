from typing import ClassVar

from notionary.blocks.rich_text.name_to_id_resolver import NameIdResolver
from notionary.blocks.rich_text.rich_text_models import (
    MentionDate,
    MentionType,
    RichTextObject,
    RichTextType,
)
from notionary.blocks.types import BlockColor


class RichTextToMarkdownConverter:
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(self, resolver: NameIdResolver | None = None):
        self.resolver = resolver or NameIdResolver()

    async def to_markdown(self, rich_text: list[RichTextObject]) -> str:
        if not rich_text:
            return ""

        parts: list[str] = []

        for rich_obj in rich_text:
            formatted_text = await self._convert_rich_text_to_markdown(rich_obj)
            parts.append(formatted_text)

        return "".join(parts)

    async def _convert_rich_text_to_markdown(self, obj: RichTextObject) -> str:
        if obj.type == RichTextType.EQUATION and obj.equation:
            return f"${obj.equation.expression}$"

        if obj.type == RichTextType.MENTION:
            mention_markdown = await self._extract_mention_markdown(obj)
            if mention_markdown:
                return mention_markdown

        content = obj.plain_text or (obj.text.content if obj.text else "")
        return self._apply_text_formatting_to_content(obj, content)

    async def _extract_mention_markdown(self, obj: RichTextObject) -> str | None:
        if not obj.mention:
            return None

        mention = obj.mention

        if mention.type == MentionType.PAGE and mention.page:
            return await self._extract_page_mention_markdown(mention.page.id)

        elif mention.type == MentionType.DATABASE and mention.database:
            return await self._extract_database_mention_markdown(mention.database.id)

        elif mention.type == MentionType.USER and mention.user:
            return await self._extract_user_mention_markdown(mention.user.id)

        elif mention.type == MentionType.DATE and mention.date:
            return self._extract_date_mention_markdown(mention.date)

        return None

    async def _extract_page_mention_markdown(self, page_id: str) -> str:
        page_name = await self.resolver.resolve_page_name(page_id)
        return f"@page[{page_name or page_id}]"

    async def _extract_database_mention_markdown(self, database_id: str) -> str:
        database_name = await self.resolver.resolve_database_name(database_id)
        return f"@database[{database_name or database_id}]"

    async def _extract_user_mention_markdown(self, user_id: str) -> str:
        user_name = await self.resolver.resolve_user_name(user_id)
        return f"@user[{user_name or user_id}]"

    def _extract_date_mention_markdown(self, date_mention: MentionDate) -> str:
        date_range = date_mention.start
        if date_mention.end:
            date_range += f"–{date_mention.end}"
        return date_range

    def _apply_text_formatting_to_content(self, obj: RichTextObject, content: str) -> str:
        if obj.text and obj.text.link:
            content = f"[{content}]({obj.text.link.url})"

        if not obj.annotations:
            return content

        annotations = obj.annotations

        if annotations.code:
            content = f"`{content}`"
        if annotations.strikethrough:
            content = f"~~{content}~~"
        if annotations.underline:
            content = f"__{content}__"
        if annotations.italic:
            content = f"*{content}*"
        if annotations.bold:
            content = f"**{content}**"

        if annotations.color != BlockColor.DEFAULT and annotations.color in self.VALID_COLORS:
            content = f"({annotations.color}:{content})"

        return content
