import pytest

from notionary.blocks.markdown.nodes import (
    AudioMarkdownNode,
    BookmarkMarkdownNode,
    BreadcrumbMarkdownNode,
    BulletedListMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    ColumnMarkdownNode,
    DividerMarkdownNode,
    EmbedMarkdownNode,
    EquationMarkdownNode,
    FileMarkdownNode,
    HeadingMarkdownNode,
    ImageMarkdownNode,
    NumberedListMarkdownNode,
    ParagraphMarkdownNode,
    QuoteMarkdownNode,
    TableMarkdownNode,
    TableOfContentsMarkdownNode,
    TodoMarkdownNode,
    ToggleableHeadingMarkdownNode,
    ToggleMarkdownNode,
    VideoMarkdownNode,
)


def test_audio_markdown_node() -> None:
    audio = AudioMarkdownNode(url="https://example.com/audio.mp3")
    expected = "[audio](https://example.com/audio.mp3)"
    assert audio.to_markdown() == expected

    audio_with_caption = AudioMarkdownNode(url="https://example.com/audio.mp3", caption="My Audio File")
    expected = "[audio](https://example.com/audio.mp3)(caption:My Audio File)"
    assert audio_with_caption.to_markdown() == expected


def test_bookmark_markdown_node() -> None:
    bookmark = BookmarkMarkdownNode(url="https://example.com")
    expected = "[bookmark](https://example.com)"
    assert bookmark.to_markdown() == expected

    # Test mit Caption - NEUE SYNTAX: (caption:...)
    bookmark_with_caption = BookmarkMarkdownNode(url="https://example.com", caption="Example Site")
    expected = "[bookmark](https://example.com)(caption:Example Site)"
    assert bookmark_with_caption.to_markdown() == expected


def test_bulleted_list_markdown_node() -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"])
    expected = "- Item 1\n- Item 2\n- Item 3"
    assert bulleted_list.to_markdown() == expected


def test_callout_markdown_node() -> None:
    callout = CalloutMarkdownNode(text="This is important")
    expected = "::: callout\nThis is important\n:::"
    assert callout.to_markdown() == expected

    # Test mit Custom Emoji
    callout_with_emoji = CalloutMarkdownNode(text="Warning!", emoji="⚠️")
    expected = "::: callout ⚠️\nWarning!\n:::"
    assert callout_with_emoji.to_markdown() == expected


def test_code_markdown_node() -> None:
    code = CodeMarkdownNode(code="print('Hello World')")
    expected = "```\nprint('Hello World')\n```"
    assert code.to_markdown() == expected

    # Test mit Language
    code_with_lang = CodeMarkdownNode(code="print('Hello World')", language="python")
    expected = "```python\nprint('Hello World')\n```"
    assert code_with_lang.to_markdown() == expected

    # Test mit Caption - NEUE SYNTAX: Caption in Quotes auf erster Zeile!
    code_with_caption = CodeMarkdownNode(code="print('Hello World')", language="python", caption="Example code")
    expected = "```python \"Example code\"\nprint('Hello World')\n```"
    assert code_with_caption.to_markdown() == expected


def test_divider_markdown_node() -> None:
    divider = DividerMarkdownNode()
    expected = "---"
    assert divider.to_markdown() == expected


def test_file_markdown_node() -> None:
    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = "[file](https://example.com/doc.pdf)"
    assert file.to_markdown() == expected

    file_with_caption = FileMarkdownNode(url="https://example.com/doc.pdf", caption="Important Document")
    expected = "[file](https://example.com/doc.pdf)(caption:Important Document)"
    assert file_with_caption.to_markdown() == expected


def test_embed_markdown_node() -> None:
    embed = EmbedMarkdownNode(url="https://example.com")
    expected = "[embed](https://example.com)"
    assert embed.to_markdown() == expected

    embed_with_caption = EmbedMarkdownNode(url="https://example.com", caption="External content")
    expected = '[embed](https://example.com "External content")'
    assert embed_with_caption.to_markdown() == expected


def test_heading_markdown_node() -> None:
    h1 = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = "# Heading 1"
    assert h1.to_markdown() == expected

    h2 = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = "## Heading 2"
    assert h2.to_markdown() == expected

    h3 = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = "### Heading 3"
    assert h3.to_markdown() == expected

    with pytest.raises(ValueError):
        HeadingMarkdownNode(text="Invalid", level=4)


def test_image_markdown_node() -> None:
    """Test ImageMarkdownNode"""
    image = ImageMarkdownNode(url="https://example.com/image.jpg")
    expected = "[image](https://example.com/image.jpg)"
    assert image.to_markdown() == expected

    image_with_caption = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image")
    expected = "[image](https://example.com/image.jpg)(caption:My Image)"
    assert image_with_caption.to_markdown() == expected

    image_full = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image", alt="Alternative text")
    expected = "[image](https://example.com/image.jpg)(caption:My Image)"
    assert image_full.to_markdown() == expected

    image_empty = ImageMarkdownNode(url="https://example.com/image.jpg", caption="")
    expected = "[image](https://example.com/image.jpg)"
    assert image_empty.to_markdown() == expected


def test_numbered_list_markdown_node() -> None:
    numbered_list = NumberedListMarkdownNode(texts=["First", "Second", "Third"])
    expected = "1. First\n2. Second\n3. Third"
    assert numbered_list.to_markdown() == expected


def test_paragraph_markdown_node() -> None:
    """Test ParagraphMarkdownNode"""
    paragraph = ParagraphMarkdownNode(text="This is a paragraph.")
    expected = "This is a paragraph."
    assert paragraph.to_markdown() == expected


def test_quote_markdown_node() -> None:
    quote = QuoteMarkdownNode(text="This is a quote")
    expected = "> This is a quote"
    assert quote.to_markdown() == expected

    quote_with_author = QuoteMarkdownNode(text="Life is beautiful")
    expected = "> Life is beautiful"
    assert quote_with_author.to_markdown() == expected


def test_table_markdown_node() -> None:
    """Test TableMarkdownNode"""
    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )
    expected = (
        "| Name | Age | City |\n| -------- | -------- | -------- |\n| Alice | 25 | Berlin |\n| Bob | 30 | Munich |"
    )
    assert table.to_markdown() == expected


def test_todo_markdown_node() -> None:
    """Test TodoMarkdownNode"""
    todo = TodoMarkdownNode(text="Buy groceries", checked=False)
    expected = "- [ ] Buy groceries"
    assert todo.to_markdown() == expected

    todo_done = TodoMarkdownNode(text="Finish homework", checked=True)
    expected = "- [x] Finish homework"
    assert todo_done.to_markdown() == expected

    todo_star = TodoMarkdownNode(text="Important task", checked=False, marker="*")
    expected = "* [ ] Important task"
    assert todo_star.to_markdown() == expected


def test_toggle_markdown_node() -> None:
    """Test ToggleMarkdownNode - FIXED"""
    # Test ohne Content - FIXED: Uses correct syntax WITH space
    toggle = ToggleMarkdownNode(title="Details", children=[])
    expected = "+++ Details\n+++"
    assert toggle.to_markdown() == expected

    # Test mit Content
    line1_node = ParagraphMarkdownNode(text="Line 1")
    line2_node = ParagraphMarkdownNode(text="Line 2")

    toggle_with_content = ToggleMarkdownNode(
        title="More Info",
        children=[line1_node, line2_node],
    )
    expected = "+++ More Info\nLine 1\n\nLine 2\n+++"
    assert toggle_with_content.to_markdown() == expected


def test_toggleable_heading_markdown_node() -> None:
    toggleable_h1 = ToggleableHeadingMarkdownNode(text="Section 1", level=1, children=[])
    expected = "+++# Section 1\n+++"
    assert toggleable_h1.to_markdown() == expected

    # Test mit Content - korrekte Syntax mit +++
    toggleable_h2 = ToggleableHeadingMarkdownNode(
        text="Section 2",
        level=2,
        children=[
            ParagraphMarkdownNode(text="Content line 1"),
            ParagraphMarkdownNode(text="Content line 2"),
        ],
    )
    expected = "+++## Section 2\nContent line 1\n\nContent line 2\n+++"
    assert toggleable_h2.to_markdown() == expected

    # Test ungültiges Level
    with pytest.raises(ValueError):
        ToggleableHeadingMarkdownNode(text="Invalid", level=4, children=[])


def test_video_markdown_node() -> None:
    """Test VideoMarkdownNode"""
    # Test ohne Caption
    video = VideoMarkdownNode(url="https://youtube.com/watch?v=123")
    expected = "[video](https://youtube.com/watch?v=123)"
    assert video.to_markdown() == expected

    # Test mit Caption - NEUE SYNTAX: (caption:...)
    video_with_caption = VideoMarkdownNode(url="https://youtube.com/watch?v=123", caption="Tutorial Video")
    expected = "[video](https://youtube.com/watch?v=123)(caption:Tutorial Video)"
    assert video_with_caption.to_markdown() == expected


def test_breadcrumb_markdown_node():
    breadcrumb = BreadcrumbMarkdownNode()
    expected = "[breadcrumb]"
    assert breadcrumb.to_markdown() == expected


def test_table_of_contents_markdown_node():
    """Test TableOfContentsMarkdownNode"""
    # Test ohne color (default)
    toc = TableOfContentsMarkdownNode()
    expected = "[toc]"
    assert toc.to_markdown() == expected

    # Simplified: TableOfContents no longer supports color parameter
    # All variations now produce the same output
    toc2 = TableOfContentsMarkdownNode()
    expected = "[toc]"
    assert toc2.to_markdown() == expected


def test_column_markdown_node():
    # Test ohne children
    column_empty = ColumnMarkdownNode(children=[])
    expected = "::: column\n:::"
    assert column_empty.to_markdown() == expected

    # Test mit content - muss genau schauen was die Implementierung macht
    children = [
        HeadingMarkdownNode(text="Column Title", level=2),
        ParagraphMarkdownNode(text="Column content here"),
    ]
    column_with_content = ColumnMarkdownNode(children=children)
    # Basiert auf der ursprünglichen Test-Expectation, aber angepasst für echte Implementierung
    expected = "::: column\n## Column Title\n\nColumn content here\n:::"
    assert column_with_content.to_markdown() == expected


def test_equation_markdown_node():
    """Test EquationMarkdownNode"""
    equation_simple = EquationMarkdownNode(expression="E = mc^2")
    expected = "$$E = mc^2$$"
    assert equation_simple.to_markdown() == expected

    equation_with_parens = EquationMarkdownNode(expression="f(x) = sin(x)")
    expected = "$$f(x) = sin(x)$$"
    assert equation_with_parens.to_markdown() == expected

    equation_with_quotes = EquationMarkdownNode(expression='say "hello"')
    expected = '$$say "hello"$$'
    assert equation_with_quotes.to_markdown() == expected

    equation_empty = EquationMarkdownNode(expression="")
    expected = "$$$$"
    assert equation_empty.to_markdown() == expected

    equation_whitespace = EquationMarkdownNode(expression="   ")
    expected = "$$$$"
    assert equation_whitespace.to_markdown() == expected


def test_pdf_markdown_node():
    """Test PdfMarkdownNode"""
    from notionary.blocks.markdown.nodes.pdf import PdfMarkdownNode

    # Test ohne Caption
    pdf = PdfMarkdownNode(url="https://example.com/document.pdf")
    expected = "[pdf](https://example.com/document.pdf)"
    assert pdf.to_markdown() == expected

    # Test mit Caption - NEUE SYNTAX: (caption:...)
    pdf_with_caption = PdfMarkdownNode(url="https://example.com/document.pdf", caption="Critical safety information")
    expected = "[pdf](https://example.com/document.pdf)(caption:Critical safety information)"
    assert pdf_with_caption.to_markdown() == expected
