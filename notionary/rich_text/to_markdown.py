from notionary.rich_text.schemas import (
    DatabaseMention,
    DateMention,
    LinkPreviewMention,
    PageMention,
    RichText,
    RichTextType,
    UserMention,
)


def rich_text_to_markdown(rich_texts: list[RichText]) -> str:
    return "".join(_convert_element(rt) for rt in rich_texts)


def _convert_element(rt: RichText) -> str:
    match rt.type:
        case RichTextType.EQUATION:
            return _convert_equation(rt)
        case RichTextType.MENTION:
            return _convert_mention(rt)
        case _:
            return _convert_text(rt)


def _convert_equation(rt: RichText) -> str:
    expr = rt.equation.expression if rt.equation else rt.plain_text
    return f"${expr}$"


def _convert_text(rt: RichText) -> str:
    content = rt.text.content if rt.text else rt.plain_text
    ann = rt.annotations

    if rt.text and rt.text.link:
        content = f"[{content}]({rt.text.link.url})"

    if ann.code:
        content = f"`{content}`"
    else:
        if ann.strikethrough:
            content = f"~~{content}~~"
        if ann.bold and ann.italic:
            content = f"***{content}***"
        elif ann.bold:
            content = f"**{content}**"
        elif ann.italic:
            content = f"*{content}*"
        if ann.underline:
            content = f'<span underline="true">{content}</span>'

    if ann.color and ann.color != "default":
        content = f'<span color="{ann.color}">{content}</span>'

    return content


def _convert_mention(rt: RichText) -> str:
    mention = rt.mention
    if mention is None:
        return rt.plain_text

    if isinstance(mention, PageMention):
        url = rt.href or mention.page.id
        return f'<mention-page url="{url}">{rt.plain_text}</mention-page>'

    if isinstance(mention, UserMention):
        url = rt.href or mention.user.id
        return f'<mention-user url="{url}">{rt.plain_text}</mention-user>'

    if isinstance(mention, DatabaseMention):
        url = rt.href or mention.database.id
        return f'<mention-database url="{url}">{rt.plain_text}</mention-database>'

    if isinstance(mention, DateMention):
        d = mention.date
        parts = [f'start="{d.start}"']
        if d.end:
            parts.append(f'end="{d.end}"')
        if d.time_zone:
            parts.append(f'timeZone="{d.time_zone}"')
        return f"<mention-date {' '.join(parts)}/>"

    if isinstance(mention, LinkPreviewMention):
        url = mention.link_preview.url
        return f"[{rt.plain_text}]({url})"

    return rt.plain_text
