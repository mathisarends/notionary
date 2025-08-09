import re
from typing import Any
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class TextInlineFormatter:
    FORMAT_PATTERNS: list[tuple[str, dict[str, Any]]] = [
        (r"\*\*(.+?)\*\*", {"bold": True}),
        (r"\*(.+?)\*", {"italic": True}),
        (r"_(.+?)_", {"italic": True}),
        (r"__(.+?)__", {"underline": True}),
        (r"~~(.+?)~~", {"strikethrough": True}),
        (r"`(.+?)`", {"code": True}),
        (r"\[(.+?)\]\((.+?)\)", {"link": True}),
        (r"@\[([0-9a-f-]+)\]", {"mention_page": True}),  # weiterhin deine Kurzsyntax
    ]

    @classmethod
    def parse_inline_formatting(cls, text: str) -> list[RichTextObject]:
        if not text:
            return []
        return cls._split_text_into_segments(text, cls.FORMAT_PATTERNS)

    @classmethod
    def _split_text_into_segments(
        cls, text: str, patterns: list[tuple[str, dict[str, Any]]]
    ) -> list[RichTextObject]:
        segs: list[RichTextObject] = []
        remaining = text

        while remaining:
            match, fmt, pos = None, None, len(remaining)
            for pattern, f in patterns:
                m = re.search(pattern, remaining)
                if m and m.start() < pos:
                    match, fmt, pos = m, f, m.start()

            if not match:
                segs.append(RichTextObject.from_plain_text(remaining))
                break

            if pos > 0:
                segs.append(RichTextObject.from_plain_text(remaining[:pos]))

            if "link" in fmt:
                segs.append(RichTextObject.for_link(match.group(1), match.group(2)))
            elif "mention_page" in fmt:
                segs.append(RichTextObject.mention_page(match.group(1)))
            elif "code" in fmt:
                segs.append(RichTextObject.from_plain_text(match.group(1), code=True))
            else:
                segs.append(RichTextObject.from_plain_text(match.group(1), **fmt))

            remaining = remaining[pos + len(match.group(0)) :]

        return segs

    @classmethod
    def extract_text_with_formatting(cls, rich_text: list[RichTextObject]) -> str:
        """
        Convert a list of RichTextObjects back into Markdown inline syntax.
        """
        parts: list[str] = []

        for obj in rich_text:
            # Basisinhalt
            content = obj.plain_text or (obj.text.content if obj.text else "")

            # Equations
            if obj.type == "equation" and obj.equation:
                parts.append(f"${obj.equation.expression}$")
                continue

            # Mentions
            if obj.type == "mention" and obj.mention:
                m = obj.mention
                if m.type == "page" and m.page:
                    parts.append(f"@[{m.page.id}]")
                    continue
                elif m.type == "user" and m.user:
                    parts.append(f"@user({m.user.id})")
                    continue
                elif m.type == "database" and m.database:
                    parts.append(f"@db({m.database.id})")
                    continue
                elif m.type == "date" and m.date:
                    if m.date.end:
                        parts.append(f"{m.date.start}–{m.date.end}")
                    else:
                        parts.append(m.date.start)
                    continue
                elif m.type == "link_preview" and m.link_preview:
                    # Als Link rendern
                    content = f"[{content}]({m.link_preview.url})"
                elif m.type == "template_mention" and m.template_mention:
                    tm = m.template_mention.type
                    parts.append(
                        "@template_user"
                        if tm == "template_mention_user"
                        else "@template_date"
                    )
                    continue

            # Normale Links (text.link)
            if obj.text and obj.text.link:
                url = obj.text.link.url
                content = f"[{content}]({url})"

            # Inline-Formatierungen
            ann = obj.annotations.model_dump() if obj.annotations else {}
            if ann.get("code"):
                content = f"`{content}`"
            if ann.get("strikethrough"):
                content = f"~~{content}~~"
            if ann.get("underline"):
                content = f"__{content}__"
            if ann.get("italic"):
                content = f"*{content}*"
            if ann.get("bold"):
                content = f"**{content}**"

            parts.append(content)

        return "".join(parts)
