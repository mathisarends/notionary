from enum import StrEnum


class RichTextPatterns(StrEnum):
    BOLD = r"\*\*(.+?)\*\*"
    """Matches **bold text**. Example: `**Hello**` → bolded "Hello"."""

    ITALIC = r"\*(.+?)\*"
    """Matches *italic text*. Example: `*Hello*` → italic "Hello"."""

    ITALIC_UNDERSCORE = r"_([^_]+?)_"
    """Matches _italic text_ using underscores. Example: `_Hello_` → italic "Hello"."""

    UNDERLINE = r"__(.+?)__"
    """Matches __underlined text__. Example: `__Hello__` → underlined "Hello"."""

    STRIKETHROUGH = r"~~(.+?)~~"
    """Matches ~~strikethrough~~ text. Example: `~~Hello~~` → struck-through "Hello"."""

    CODE = r"`(.+?)`"
    """Matches inline code. Example: `` `print("Hi")` `` → code span `print("Hi")`."""

    LINK = r"\[(.+?)\]\((.+?)\)"
    """Matches a hyperlink. Example: `[Google](https://google.com)` → link with label "Google"."""

    INLINE_EQUATION = r"\$(.+?)\$"
    """Matches an inline LaTeX equation. Example: `$E=mc^2$` → math formula E=mc²."""

    COLOR = r"\((\w+):(.+?)\)"
    """Matches colored text. Example: `(red:Important)` → text "Important" colored red."""

    PAGE_MENTION = r"@page\[([^\]]+)\]"
    """Matches a Notion page mention by name or ID. Example: `@page[My Page]`."""

    DATABASE_MENTION = r"@database\[([^\]]+)\]"
    """Matches a Notion database mention by name or ID. Example: `@database[Tasks]`."""

    DATASOURCE_MENTION = r"@datasource\[([^\]]+)\]"
    """Matches a Notion data source mention by name or ID. Example: `@datasource[My Data]`."""

    USER_MENTION = r"@user\[([^\]]+)\]"
    """Matches a Notion user mention by name or ID. Example: `@user[Some Person]`."""
