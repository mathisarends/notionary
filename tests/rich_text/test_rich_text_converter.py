from notionary.rich_text.schemas import (
    DatabaseMention,
    DateMention,
    EquationObject,
    LinkObject,
    LinkPreviewMention,
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
from notionary.rich_text.to_markdown import rich_text_to_markdown
from notionary.rich_text.to_rich_text import markdown_to_rich_text


class TestRichTextToMarkdown:
    def test_empty_list(self) -> None:
        assert rich_text_to_markdown([]) == ""

    def test_plain_text(self) -> None:
        rt = [RichText.from_plain_text("Hello world")]
        assert rich_text_to_markdown(rt) == "Hello world"

    def test_bold(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Bold",
                text=TextContent(content="Bold"),
                annotations=TextAnnotations(bold=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "**Bold**"

    def test_italic(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Italic",
                text=TextContent(content="Italic"),
                annotations=TextAnnotations(italic=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "*Italic*"

    def test_bold_italic(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Both",
                text=TextContent(content="Both"),
                annotations=TextAnnotations(bold=True, italic=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "***Both***"

    def test_strikethrough(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Struck",
                text=TextContent(content="Struck"),
                annotations=TextAnnotations(strikethrough=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "~~Struck~~"

    def test_code(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="code",
                text=TextContent(content="code"),
                annotations=TextAnnotations(code=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "`code`"

    def test_underline(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="underlined",
                text=TextContent(content="underlined"),
                annotations=TextAnnotations(underline=True),
            )
        ]
        assert rich_text_to_markdown(rt) == '<span underline="true">underlined</span>'

    def test_link(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Google",
                text=TextContent(
                    content="Google", link=LinkObject(url="https://google.com")
                ),
            )
        ]
        assert rich_text_to_markdown(rt) == "[Google](https://google.com)"

    def test_color(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Red",
                text=TextContent(content="Red"),
                annotations=TextAnnotations(color="red"),
            )
        ]
        assert rich_text_to_markdown(rt) == '<span color="red">Red</span>'

    def test_equation(self) -> None:
        rt = [
            RichText(
                type=RichTextType.EQUATION,
                plain_text="E=mc^2",
                equation=EquationObject(expression="E=mc^2"),
            )
        ]
        assert rich_text_to_markdown(rt) == "$E=mc^2$"

    def test_page_mention_with_href(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="My Page",
                mention=PageMention(page=MentionPageRef(id="abc123")),
                href="https://notion.so/My-Page-abc123",
            )
        ]
        result = rich_text_to_markdown(rt)
        assert (
            result
            == '<mention-page url="https://notion.so/My-Page-abc123">My Page</mention-page>'
        )

    def test_page_mention_without_href(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="My Page",
                mention=PageMention(page=MentionPageRef(id="abc-123")),
            )
        ]
        result = rich_text_to_markdown(rt)
        assert result == '<mention-page url="abc-123">My Page</mention-page>'

    def test_user_mention(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="John",
                mention=UserMention(user=MentionUserRef(id="user-1")),
                href="https://notion.so/user-1",
            )
        ]
        result = rich_text_to_markdown(rt)
        assert (
            result == '<mention-user url="https://notion.so/user-1">John</mention-user>'
        )

    def test_database_mention(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="Tasks DB",
                mention=DatabaseMention(database=MentionDatabaseRef(id="db-1")),
                href="https://notion.so/db-1",
            )
        ]
        result = rich_text_to_markdown(rt)
        assert (
            result
            == '<mention-database url="https://notion.so/db-1">Tasks DB</mention-database>'
        )

    def test_date_mention_start_only(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=DateMention(date=MentionDate(start="2024-01-15")),
            )
        ]
        assert rich_text_to_markdown(rt) == '<mention-date start="2024-01-15"/>'

    def test_date_mention_with_end(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=DateMention(
                    date=MentionDate(start="2024-01-15", end="2024-01-20")
                ),
            )
        ]
        assert (
            rich_text_to_markdown(rt)
            == '<mention-date start="2024-01-15" end="2024-01-20"/>'
        )

    def test_date_mention_with_timezone(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=DateMention(
                    date=MentionDate(start="2024-01-15", time_zone="Europe/Berlin")
                ),
            )
        ]
        assert (
            rich_text_to_markdown(rt)
            == '<mention-date start="2024-01-15" timeZone="Europe/Berlin"/>'
        )

    def test_mixed_content(self) -> None:
        rt = [
            RichText.from_plain_text("Hello "),
            RichText(
                type=RichTextType.TEXT,
                plain_text="world",
                text=TextContent(content="world"),
                annotations=TextAnnotations(bold=True),
            ),
        ]
        assert rich_text_to_markdown(rt) == "Hello **world**"

    def test_code_skips_bold_italic(self) -> None:
        rt = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="x",
                text=TextContent(content="x"),
                annotations=TextAnnotations(code=True, bold=True, italic=True),
            )
        ]
        assert rich_text_to_markdown(rt) == "`x`"

    def test_link_preview_mention(self) -> None:
        rt = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="Preview",
                mention=LinkPreviewMention(
                    link_preview=LinkObject(url="https://example.com")
                ),
            )
        ]
        assert rich_text_to_markdown(rt) == "[Preview](https://example.com)"


class TestMarkdownToRichText:
    def test_empty_string(self) -> None:
        assert markdown_to_rich_text("") == []

    def test_plain_text(self) -> None:
        result = markdown_to_rich_text("Hello world")
        assert len(result) == 1
        assert result[0].plain_text == "Hello world"
        assert result[0].type == RichTextType.TEXT

    def test_bold(self) -> None:
        result = markdown_to_rich_text("**bold**")
        assert len(result) == 1
        assert result[0].plain_text == "bold"
        assert result[0].annotations.bold is True

    def test_italic(self) -> None:
        result = markdown_to_rich_text("*italic*")
        assert len(result) == 1
        assert result[0].plain_text == "italic"
        assert result[0].annotations.italic is True

    def test_bold_italic(self) -> None:
        result = markdown_to_rich_text("***both***")
        assert len(result) == 1
        assert result[0].plain_text == "both"
        assert result[0].annotations.bold is True
        assert result[0].annotations.italic is True

    def test_strikethrough(self) -> None:
        result = markdown_to_rich_text("~~struck~~")
        assert len(result) == 1
        assert result[0].plain_text == "struck"
        assert result[0].annotations.strikethrough is True

    def test_code(self) -> None:
        result = markdown_to_rich_text("`code`")
        assert len(result) == 1
        assert result[0].plain_text == "code"
        assert result[0].annotations.code is True

    def test_underline(self) -> None:
        result = markdown_to_rich_text('<span underline="true">underlined</span>')
        assert len(result) == 1
        assert result[0].plain_text == "underlined"
        assert result[0].annotations.underline is True

    def test_color(self) -> None:
        result = markdown_to_rich_text('<span color="red">Important</span>')
        assert len(result) == 1
        assert result[0].plain_text == "Important"
        assert result[0].annotations.color == "red"

    def test_link(self) -> None:
        result = markdown_to_rich_text("[Google](https://google.com)")
        assert len(result) == 1
        assert result[0].plain_text == "Google"
        assert result[0].text.link.url == "https://google.com"
        assert result[0].href == "https://google.com"

    def test_equation(self) -> None:
        result = markdown_to_rich_text("$E=mc^2$")
        assert len(result) == 1
        assert result[0].type == RichTextType.EQUATION
        assert result[0].equation.expression == "E=mc^2"

    def test_line_break(self) -> None:
        result = markdown_to_rich_text("before<br>after")
        assert len(result) == 3
        assert result[0].plain_text == "before"
        assert result[1].plain_text == "\n"
        assert result[2].plain_text == "after"

    def test_page_mention(self) -> None:
        result = markdown_to_rich_text(
            '<mention-page url="https://notion.so/abc123">My Page</mention-page>'
        )
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert isinstance(result[0].mention, PageMention)
        assert result[0].plain_text == "My Page"

    def test_page_mention_self_closing(self) -> None:
        result = markdown_to_rich_text('<mention-page url="abc123"/>')
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert isinstance(result[0].mention, PageMention)

    def test_user_mention(self) -> None:
        result = markdown_to_rich_text(
            '<mention-user url="https://notion.so/user-1">John</mention-user>'
        )
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert isinstance(result[0].mention, UserMention)
        assert result[0].plain_text == "John"

    def test_database_mention(self) -> None:
        result = markdown_to_rich_text(
            '<mention-database url="https://notion.so/db-1">Tasks</mention-database>'
        )
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert isinstance(result[0].mention, DatabaseMention)
        assert result[0].plain_text == "Tasks"

    def test_date_mention_start_only(self) -> None:
        result = markdown_to_rich_text('<mention-date start="2024-01-15"/>')
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert isinstance(result[0].mention, DateMention)
        assert result[0].mention.date.start == "2024-01-15"

    def test_date_mention_with_end(self) -> None:
        result = markdown_to_rich_text(
            '<mention-date start="2024-01-15" end="2024-01-20"/>'
        )
        assert len(result) == 1
        assert isinstance(result[0].mention, DateMention)
        assert result[0].mention.date.start == "2024-01-15"
        assert result[0].mention.date.end == "2024-01-20"
        assert result[0].plain_text == "2024-01-15\u20132024-01-20"

    def test_mixed_content(self) -> None:
        result = markdown_to_rich_text("Hello **bold** world")
        assert len(result) == 3
        assert result[0].plain_text == "Hello "
        assert result[0].annotations.bold is False
        assert result[1].plain_text == "bold"
        assert result[1].annotations.bold is True
        assert result[2].plain_text == " world"
        assert result[2].annotations.bold is False

    def test_uuid_extraction_from_notion_url(self) -> None:
        result = markdown_to_rich_text(
            '<mention-page url="https://notion.so/My-Page-abc123def456abc123def456abc123de">Title</mention-page>'
        )
        assert isinstance(result[0].mention, PageMention)
        assert result[0].mention.page.id == "abc123de-f456-abc1-23de-f456abc123de"

    def test_uuid_passthrough(self) -> None:
        result = markdown_to_rich_text(
            '<mention-page url="abc123de-f456-abc1-23de-f456abc123de">Title</mention-page>'
        )
        assert isinstance(result[0].mention, PageMention)
        assert result[0].mention.page.id == "abc123de-f456-abc1-23de-f456abc123de"


class TestRoundTrip:
    """Verify that converting to markdown and back preserves meaning."""

    def test_plain_text_roundtrip(self) -> None:
        original = [RichText.from_plain_text("Hello world")]
        md = rich_text_to_markdown(original)
        result = markdown_to_rich_text(md)
        assert result[0].plain_text == "Hello world"

    def test_bold_roundtrip(self) -> None:
        original = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="bold",
                text=TextContent(content="bold"),
                annotations=TextAnnotations(bold=True),
            )
        ]
        md = rich_text_to_markdown(original)
        result = markdown_to_rich_text(md)
        assert result[0].plain_text == "bold"
        assert result[0].annotations.bold is True

    def test_equation_roundtrip(self) -> None:
        original = [
            RichText(
                type=RichTextType.EQUATION,
                plain_text="x^2",
                equation=EquationObject(expression="x^2"),
            )
        ]
        md = rich_text_to_markdown(original)
        result = markdown_to_rich_text(md)
        assert result[0].type == RichTextType.EQUATION
        assert result[0].equation.expression == "x^2"

    def test_link_roundtrip(self) -> None:
        original = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Link",
                text=TextContent(
                    content="Link", link=LinkObject(url="https://example.com")
                ),
            )
        ]
        md = rich_text_to_markdown(original)
        result = markdown_to_rich_text(md)
        assert result[0].plain_text == "Link"
        assert result[0].text.link.url == "https://example.com"

    def test_date_mention_roundtrip(self) -> None:
        original = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=DateMention(
                    date=MentionDate(start="2024-01-15", end="2024-01-20")
                ),
            )
        ]
        md = rich_text_to_markdown(original)
        result = markdown_to_rich_text(md)
        assert isinstance(result[0].mention, DateMention)
        assert result[0].mention.date.start == "2024-01-15"
        assert result[0].mention.date.end == "2024-01-20"


class TestRichTextSchemas:
    def test_from_plain_text_factory(self) -> None:
        rt = RichText.from_plain_text("hello")
        assert rt.type == RichTextType.TEXT
        assert rt.plain_text == "hello"
        assert rt.text.content == "hello"
        assert rt.annotations.bold is False

    def test_deserialize_text_from_notion_api(self) -> None:
        api_data = {
            "type": "text",
            "text": {"content": "Hello", "link": None},
            "annotations": {
                "bold": True,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "Hello",
            "href": None,
        }
        rt = RichText.model_validate(api_data)
        assert rt.type == RichTextType.TEXT
        assert rt.plain_text == "Hello"
        assert rt.annotations.bold is True
        assert rt.text.content == "Hello"

    def test_deserialize_equation_from_notion_api(self) -> None:
        api_data = {
            "type": "equation",
            "equation": {"expression": "E=mc^2"},
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "E=mc^2",
            "href": None,
        }
        rt = RichText.model_validate(api_data)
        assert rt.type == RichTextType.EQUATION
        assert rt.equation.expression == "E=mc^2"

    def test_deserialize_page_mention_from_notion_api(self) -> None:
        api_data = {
            "type": "mention",
            "mention": {
                "type": "page",
                "page": {"id": "abc-123"},
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "Linked Page",
            "href": "https://notion.so/abc-123",
        }
        rt = RichText.model_validate(api_data)
        assert rt.type == RichTextType.MENTION
        assert isinstance(rt.mention, PageMention)
        assert rt.mention.page.id == "abc-123"

    def test_deserialize_user_mention_from_notion_api(self) -> None:
        api_data = {
            "type": "mention",
            "mention": {
                "type": "user",
                "user": {"object": "user", "id": "user-1", "name": "John"},
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "John",
            "href": None,
        }
        rt = RichText.model_validate(api_data)
        assert rt.type == RichTextType.MENTION
        assert isinstance(rt.mention, UserMention)
        assert rt.mention.user.id == "user-1"

    def test_deserialize_date_mention_from_notion_api(self) -> None:
        api_data = {
            "type": "mention",
            "mention": {
                "type": "date",
                "date": {"start": "2024-01-15", "end": None, "time_zone": None},
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "2024-01-15",
            "href": None,
        }
        rt = RichText.model_validate(api_data)
        assert rt.type == RichTextType.MENTION
        assert isinstance(rt.mention, DateMention)
        assert rt.mention.date.start == "2024-01-15"
