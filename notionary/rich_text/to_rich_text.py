import re

from notionary.rich_text.schemas import (
    DatabaseMention,
    DateMention,
    EquationObject,
    LinkObject,
    MentionDatabaseRef,
    MentionDate,
    MentionPageRef,
    MentionUserRef,
    PageMention,
    RichText,
    RichTextType,
    TextAnnotations,
    TextContent,
    UserMention,
)

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "mention_page",
        re.compile(r'<mention-page\s+url="([^"]*)">(.*?)</mention-page>', re.DOTALL),
    ),
    ("mention_page_sc", re.compile(r'<mention-page\s+url="([^"]*)"\s*/>')),
    (
        "mention_user",
        re.compile(r'<mention-user\s+url="([^"]*)">(.*?)</mention-user>', re.DOTALL),
    ),
    ("mention_user_sc", re.compile(r'<mention-user\s+url="([^"]*)"\s*/>')),
    (
        "mention_db",
        re.compile(
            r'<mention-database\s+url="([^"]*)">(.*?)</mention-database>', re.DOTALL
        ),
    ),
    ("mention_db_sc", re.compile(r'<mention-database\s+url="([^"]*)"\s*/>')),
    ("mention_date", re.compile(r"<mention-date\s+([^/]*?)\s*/>")),
    ("underline", re.compile(r'<span\s+underline="true">(.*?)</span>', re.DOTALL)),
    ("color", re.compile(r'<span\s+color="([^"]+)">(.*?)</span>', re.DOTALL)),
    ("br", re.compile(r"<br\s*/?>")),
    ("bold_italic", re.compile(r"\*\*\*(.+?)\*\*\*")),
    ("bold", re.compile(r"\*\*(.+?)\*\*")),
    ("italic", re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")),
    ("strikethrough", re.compile(r"~~(.+?)~~")),
    ("code", re.compile(r"`([^`]+)`")),
    ("equation", re.compile(r"\$([^$]+)\$")),
    ("link", re.compile(r"\[([^\]]+)\]\(([^)]+)\)")),
]

_ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def markdown_to_rich_text(text: str) -> list[RichText]:
    if not text:
        return []
    return _parse(text)


def _parse(text: str) -> list[RichText]:
    result: list[RichText] = []
    pos = 0

    while pos < len(text):
        earliest: re.Match[str] | None = None
        earliest_kind: str | None = None

        for kind, pattern in _PATTERNS:
            m = pattern.search(text, pos)
            if m and (earliest is None or m.start() < earliest.start()):
                earliest = m
                earliest_kind = kind

        if earliest is None or earliest_kind is None:
            remaining = text[pos:]
            if remaining:
                result.append(RichText.from_plain_text(remaining))
            break

        if earliest.start() > pos:
            result.append(RichText.from_plain_text(text[pos : earliest.start()]))

        result.append(_build(earliest_kind, earliest))
        pos = earliest.end()

    return result


def _build(kind: str, m: re.Match[str]) -> RichText:
    match kind:
        case "bold_italic":
            return _styled_text(m.group(1), bold=True, italic=True)
        case "bold":
            return _styled_text(m.group(1), bold=True)
        case "italic":
            return _styled_text(m.group(1), italic=True)
        case "strikethrough":
            return _styled_text(m.group(1), strikethrough=True)
        case "code":
            return _styled_text(m.group(1), code=True)
        case "underline":
            return _styled_text(m.group(1), underline=True)
        case "color":
            return _styled_text(m.group(2), color=m.group(1))
        case "br":
            return RichText.from_plain_text("\n")
        case "equation":
            return RichText(
                type=RichTextType.EQUATION,
                plain_text=m.group(1),
                equation=EquationObject(expression=m.group(1)),
            )
        case "link":
            url, label = m.group(2), m.group(1)
            return RichText(
                type=RichTextType.TEXT,
                plain_text=label,
                text=TextContent(content=label, link=LinkObject(url=url)),
                href=url,
            )
        case "mention_page":
            return _page_mention(m.group(1), m.group(2))
        case "mention_page_sc":
            return _page_mention(m.group(1), "")
        case "mention_user":
            return _user_mention(m.group(1), m.group(2))
        case "mention_user_sc":
            return _user_mention(m.group(1), "")
        case "mention_db":
            return _db_mention(m.group(1), m.group(2))
        case "mention_db_sc":
            return _db_mention(m.group(1), "")
        case "mention_date":
            return _date_mention(m.group(1))
        case _:
            return RichText.from_plain_text(m.group(0))


def _styled_text(
    content: str,
    *,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
) -> RichText:
    return RichText(
        type=RichTextType.TEXT,
        plain_text=content,
        text=TextContent(content=content),
        annotations=TextAnnotations(
            bold=bold,
            italic=italic,
            strikethrough=strikethrough,
            underline=underline,
            code=code,
            color=color,
        ),
    )


_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
_HEX32_EXACT_RE = re.compile(r"^[0-9a-f]{32}$", re.I)
_HEX32_END_RE = re.compile(r"(?<=[^0-9a-f])([0-9a-f]{32})$", re.I)


def _extract_id(url: str) -> str:
    if _UUID_RE.match(url):
        return url
    if _HEX32_EXACT_RE.match(url):
        return _format_uuid(url)
    last_segment = url.split("?")[0].split("#")[0].rstrip("/").rsplit("/", 1)[-1]
    m = _HEX32_END_RE.search(last_segment)
    if m:
        return _format_uuid(m.group(1))
    return url


def _format_uuid(raw: str) -> str:
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


def _page_mention(url: str, label: str) -> RichText:
    return RichText(
        type=RichTextType.MENTION,
        plain_text=label,
        mention=PageMention(page=MentionPageRef(id=_extract_id(url))),
        href=url,
    )


def _user_mention(url: str, label: str) -> RichText:
    return RichText(
        type=RichTextType.MENTION,
        plain_text=label,
        mention=UserMention(user=MentionUserRef(id=_extract_id(url))),
        href=url,
    )


def _db_mention(url: str, label: str) -> RichText:
    return RichText(
        type=RichTextType.MENTION,
        plain_text=label,
        mention=DatabaseMention(database=MentionDatabaseRef(id=_extract_id(url))),
        href=url,
    )


def _date_mention(attrs_str: str) -> RichText:
    attrs = dict(_ATTR_RE.findall(attrs_str))
    start = attrs.get("start", "")
    end = attrs.get("end")
    tz = attrs.get("timeZone")
    start_time = attrs.get("startTime")

    display = start
    if start_time:
        display = f"{start} {start_time}"
    if end:
        display = f"{start}\u2013{end}"

    return RichText(
        type=RichTextType.MENTION,
        plain_text=display,
        mention=DateMention(date=MentionDate(start=start, end=end, time_zone=tz)),
    )
