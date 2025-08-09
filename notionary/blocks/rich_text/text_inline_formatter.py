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
            content = obj.plain_text or getattr(obj.text, "content", "")

            # Mentions behandeln
            if obj.type == "mention" and hasattr(obj, "mention"):
                if obj.mention.get("type") == "page":
                    page_id = obj.mention["page"]["id"]
                    parts.append(f"@[{page_id}]")
                    continue

            # Links
            if getattr(obj.text, "link", None):
                url = obj.text.link.url
                content = f"[{content}]({url})"

            # Code zuerst, damit keine Konflikte mit anderen Markern entstehen
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
