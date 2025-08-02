"""
Tests für alle MarkdownNode-Implementierungen mit pytest.
Testet ob die to_markdown() Methode den erwarteten String zurückgibt.
"""

from notionary.blocks.audio.audio_markdown_node import AudioMarkdownNode
from notionary.blocks.bookmark.bookmark_markdown_node import BookmarkMarkdownNode
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import (
    BulletedListMarkdownNode,
)
from notionary.blocks.callout.callout_markdown_node import CalloutMarkdownNode
from notionary.blocks.code.code_markdown_node import CodeMarkdownNode
from notionary.blocks.divider.divider_markdown_node import DividerMarkdownNode
from notionary.blocks.embed.embed_markdown_node import EmbedMarkdownNode
from notionary.blocks.file.file_element_markdown_node import FileMarkdownNode
from notionary.blocks.heading.heading_markdown_node import HeadingMarkdownNode
from notionary.blocks.image_block.image_markdown_node import ImageMarkdownNode
from notionary.blocks.numbered_list.numbered_list_markdown_node import (
    NumberedListMarkdownNode,
)
from notionary.blocks.paragraph.paragraph_markdown_node import ParagraphMarkdownNode
from notionary.blocks.quote.quote_markdown_node import QuoteMarkdownNode
from notionary.blocks.table.table_markdown_node import TableMarkdownNode
from notionary.blocks.todo.todo_markdown_node import TodoMarkdownNode
from notionary.blocks.toggle.toggle_markdown_node import ToggleMarkdownNode
from notionary.blocks.toggleable_heading.toggleable_heading_markdown_node import (
    ToggleableHeadingMarkdownNode,
)
from notionary.blocks.video.video_markdown_node import VideoMarkdownNode
from notionary.markdown.markdown_node import MarkdownNode

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


def test_file_markdown_node():
    """Test FileMarkdownNode"""
    # Test ohne Caption
    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = "[file](https://example.com/doc.pdf)"
    assert file.to_markdown() == expected

    # Test mit Caption
    file_with_caption = FileMarkdownNode(
        url="https://example.com/doc.pdf", caption="Important Document"
    )
    expected = '[file](https://example.com/doc.pdf "Important Document")'
    assert file_with_caption.to_markdown() == expected


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
    expected = "[quote](Life is beautiful)"
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
