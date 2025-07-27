#!/usr/bin/env python3
"""
Tests für alle MarkdownNode-Implementierungen mit pytest.
Testet ob die to_markdown() Methode den erwarteten String zurückgibt.
"""

import sys
import os

# Füge das notionary package zum Python path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from notionary.blocks import (
    AudioMarkdownNode,
    BookmarkMarkdownNode,
    BulletedListMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    DividerMarkdownNode,
    DocumentMarkdownNode,
    EmbedMarkdownNode,
    HeadingMarkdownNode,
    ImageMarkdownNode,
    MentionMarkdownNode,
    NumberedListMarkdownNode,
    ParagraphMarkdownNode,
    QuoteMarkdownNode,
    TableMarkdownNode,
    TodoMarkdownNode,
    ToggleMarkdownNode,
    ToggleableHeadingMarkdownNode,
    VideoMarkdownNode,
)

import pytest


def test_audio_markdown_node():
    """Test AudioMarkdownNode"""
    # Test ohne Caption
    audio = AudioMarkdownNode(url="https://example.com/audio.mp3")
    expected = "[audio](https://example.com/audio.mp3)"
    assert audio.to_markdown() == expected

    # Test mit Caption
    audio_with_caption = AudioMarkdownNode(
        url="https://example.com/audio.mp3", caption="My Audio File"
    )
    expected = '[audio](https://example.com/audio.mp3 "My Audio File")'
    assert audio_with_caption.to_markdown() == expected


def test_bookmark_markdown_node():
    """Test BookmarkMarkdownNode"""
    # Test nur URL
    bookmark = BookmarkMarkdownNode(url="https://example.com")
    expected = "[bookmark](https://example.com)"
    assert bookmark.to_markdown() == expected

    # Test mit Title
    bookmark_with_title = BookmarkMarkdownNode(
        url="https://example.com", title="Example Site"
    )
    expected = '[bookmark](https://example.com "Example Site")'
    assert bookmark_with_title.to_markdown() == expected

    # Test mit Title und Description
    bookmark_full = BookmarkMarkdownNode(
        url="https://example.com", title="Example Site", description="A great example"
    )
    expected = '[bookmark](https://example.com "Example Site" "A great example")'
    assert bookmark_full.to_markdown() == expected


def test_bulleted_list_markdown_node():
    """Test BulletedListMarkdownNode"""
    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"])
    expected = "- Item 1\n- Item 2\n- Item 3"
    assert bulleted_list.to_markdown() == expected


def test_callout_markdown_node():
    """Test CalloutMarkdownNode"""
    # Test ohne Emoji (sollte default verwenden)
    callout = CalloutMarkdownNode(text="This is important")
    expected = "[callout](This is important)"
    assert callout.to_markdown() == expected

    # Test mit Custom Emoji
    callout_with_emoji = CalloutMarkdownNode(text="Warning!", emoji="⚠️")
    expected = '[callout](Warning! "⚠️")'
    assert callout_with_emoji.to_markdown() == expected


def test_code_markdown_node():
    """Test CodeMarkdownNode"""
    # Test ohne Language und Caption
    code = CodeMarkdownNode(code="print('Hello World')")
    expected = "```\nprint('Hello World')\n```"
    assert code.to_markdown() == expected

    # Test mit Language
    code_with_lang = CodeMarkdownNode(code="print('Hello World')", language="python")
    expected = "```python\nprint('Hello World')\n```"
    assert code_with_lang.to_markdown() == expected

    # Test mit Caption
    code_with_caption = CodeMarkdownNode(
        code="print('Hello World')", language="python", caption="Example code"
    )
    expected = "```python\nprint('Hello World')\n```\nCaption: Example code"
    assert code_with_caption.to_markdown() == expected


def test_divider_markdown_node():
    """Test DividerMarkdownNode"""
    divider = DividerMarkdownNode()
    expected = "---"
    assert divider.to_markdown() == expected


def test_document_markdown_node():
    """Test DocumentMarkdownNode"""
    # Test ohne Caption
    document = DocumentMarkdownNode(url="https://example.com/doc.pdf")
    expected = "[document](https://example.com/doc.pdf)"
    assert document.to_markdown() == expected

    # Test mit Caption
    document_with_caption = DocumentMarkdownNode(
        url="https://example.com/doc.pdf", caption="Important Document"
    )
    expected = '[document](https://example.com/doc.pdf "Important Document")'
    assert document_with_caption.to_markdown() == expected



def test_embed_markdown_node():
    """Test EmbedMarkdownNode"""
    # Test ohne Caption
    embed = EmbedMarkdownNode(url="https://example.com")
    expected = "[embed](https://example.com)"
    assert embed.to_markdown() == expected

    # Test mit Caption
    embed_with_caption = EmbedMarkdownNode(
        url="https://example.com", caption="External content"
    )
    expected = '[embed](https://example.com "External content")'
    assert embed_with_caption.to_markdown() == expected


def test_heading_markdown_node():
    """Test HeadingMarkdownNode"""
    # Test verschiedene Level
    h1 = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = "# Heading 1"
    assert h1.to_markdown() == expected

    h2 = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = "## Heading 2"
    assert h2.to_markdown() == expected

    h3 = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = "### Heading 3"
    assert h3.to_markdown() == expected

    # Test ungültiges Level (sollte Exception werfen)
    with pytest.raises(ValueError):
        HeadingMarkdownNode(text="Invalid", level=4)


def test_image_markdown_node():
    """Test ImageMarkdownNode"""
    # Test nur URL (ohne Caption)
    image = ImageMarkdownNode(url="https://example.com/image.jpg")
    expected = "[image](https://example.com/image.jpg)"
    assert image.to_markdown() == expected

    # Test mit Caption - Caption MUSS im Output erscheinen!
    image_with_caption = ImageMarkdownNode(
        url="https://example.com/image.jpg", caption="My Image"
    )
    expected = '[image](https://example.com/image.jpg "My Image")'
    assert image_with_caption.to_markdown() == expected

    # Test mit Caption (alt wird ignoriert)
    image_full = ImageMarkdownNode(
        url="https://example.com/image.jpg", caption="My Image", alt="Alternative text"
    )
    expected = '[image](https://example.com/image.jpg "My Image")'
    assert image_full.to_markdown() == expected

    # Test mit leerem Caption
    image_empty = ImageMarkdownNode(url="https://example.com/image.jpg", caption="")
    expected = "[image](https://example.com/image.jpg)"
    assert image_empty.to_markdown() == expected


def test_mention_markdown_node():
    """Test MentionMarkdownNode"""
    # Test Page Mention
    page_mention = MentionMarkdownNode(mention_type="page", value="123-456-789")
    expected = "@[123-456-789]"
    assert page_mention.to_markdown() == expected

    # Test Database Mention
    db_mention = MentionMarkdownNode(mention_type="database", value="db-123")
    expected = "@db[db-123]"
    assert db_mention.to_markdown() == expected

    # Test Date Mention
    date_mention = MentionMarkdownNode(mention_type="date", value="2024-01-01")
    expected = "@date[2024-01-01]"
    assert date_mention.to_markdown() == expected


def test_numbered_list_markdown_node():
    """Test NumberedListMarkdownNode"""
    numbered_list = NumberedListMarkdownNode(texts=["First", "Second", "Third"])
    expected = "1. First\n2. Second\n3. Third"
    assert numbered_list.to_markdown() == expected


def test_paragraph_markdown_node():
    """Test ParagraphMarkdownNode"""
    paragraph = ParagraphMarkdownNode(text="This is a paragraph.")
    expected = "This is a paragraph."
    assert paragraph.to_markdown() == expected


def test_quote_markdown_node():
    """Test QuoteMarkdownNode"""
    # Test ohne Author
    quote = QuoteMarkdownNode(text="This is a quote")
    expected = "[quote](This is a quote)"
    assert quote.to_markdown() == expected

    # Test mit Author
    quote_with_author = QuoteMarkdownNode(text="Life is beautiful")
    expected = '[quote](Life is beautiful)'
    assert quote_with_author.to_markdown() == expected


def test_table_markdown_node():
    """Test TableMarkdownNode"""
    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )
    expected = "| Name | Age | City |\n| -------- | -------- | -------- |\n| Alice | 25 | Berlin |\n| Bob | 30 | Munich |"
    assert table.to_markdown() == expected


def test_todo_markdown_node():
    """Test TodoMarkdownNode"""
    # Test unchecked
    todo = TodoMarkdownNode(text="Buy groceries", checked=False)
    expected = "- [ ] Buy groceries"
    assert todo.to_markdown() == expected

    # Test checked
    todo_done = TodoMarkdownNode(text="Finish homework", checked=True)
    expected = "- [x] Finish homework"
    assert todo_done.to_markdown() == expected

    # Test mit anderem Marker
    todo_star = TodoMarkdownNode(text="Important task", checked=False, marker="*")
    expected = "* [ ] Important task"
    assert todo_star.to_markdown() == expected


def test_toggle_markdown_node():
    """Test ToggleMarkdownNode"""
    # Test ohne Content
    toggle = ToggleMarkdownNode(title="Details")
    expected = "+++ Details"
    assert toggle.to_markdown() == expected

    # Test mit Content
    toggle_with_content = ToggleMarkdownNode(
        title="More Info", content=["Line 1", "Line 2"]
    )
    expected = "+++ More Info\n| Line 1\n| Line 2"
    assert toggle_with_content.to_markdown() == expected


def test_toggleable_heading_markdown_node():
    """Test ToggleableHeadingMarkdownNode"""
    # Test ohne Content
    toggleable_h1 = ToggleableHeadingMarkdownNode(text="Section 1", level=1)
    expected = "+# Section 1"
    assert toggleable_h1.to_markdown() == expected

    # Test mit Content
    toggleable_h2 = ToggleableHeadingMarkdownNode(
        text="Section 2", level=2, content=["Content line 1", "Content line 2"]
    )
    expected = "+## Section 2\n| Content line 1\n| Content line 2"
    assert toggleable_h2.to_markdown() == expected

    # Test ungültiges Level
    with pytest.raises(ValueError):
        ToggleableHeadingMarkdownNode(text="Invalid", level=4)


def test_video_markdown_node():
    """Test VideoMarkdownNode"""
    # Test ohne Caption
    video = VideoMarkdownNode(url="https://youtube.com/watch?v=123")
    expected = "[video](https://youtube.com/watch?v=123)"
    assert video.to_markdown() == expected

    # Test mit Caption
    video_with_caption = VideoMarkdownNode(
        url="https://youtube.com/watch?v=123", caption="Tutorial Video"
    )
    expected = '[video](https://youtube.com/watch?v=123 "Tutorial Video")'
    assert video_with_caption.to_markdown() == expected
