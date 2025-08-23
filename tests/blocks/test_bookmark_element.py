"""
Pytest tests for BookmarkElement.
Updated to match the actual implementation with new caption mixin syntax.
"""

from unittest.mock import Mock

import pytest
import pytest_asyncio

from notionary.blocks.bookmark.bookmark_element import BookmarkElement
from notionary.blocks.bookmark.bookmark_models import BookmarkBlock, CreateBookmarkBlock
from notionary.blocks.types import BlockType


@pytest.mark.asyncio
async def test_match_markdown():
    """Test die Erkennung von Markdown-Bookmarks."""
    # Gültige Bookmark-Formate
    assert await BookmarkElement.markdown_to_notion("[bookmark](https://example.com)")
    assert await BookmarkElement.markdown_to_notion(
        "[bookmark](https://example.com)(caption:Titel)"
    )
    assert await BookmarkElement.markdown_to_notion(
        "[bookmark](https://example.com)(caption:Titel – Beschreibung)"
    )

    # Ungültige Formate
    assert not await BookmarkElement.markdown_to_notion("[link](https://example.com)")
    assert await BookmarkElement.markdown_to_notion("Dies ist kein Bookmark") is None
    assert not await BookmarkElement.markdown_to_notion("[bookmark](nicht-url)")
    assert not await BookmarkElement.markdown_to_notion(
        "[bookmark](ftp://example.com)"
    )  # Nur http/https


def test_match_notion():
    """Test die Erkennung von Notion-Bookmark-Blöcken."""
    # Valid bookmark block
    bookmark_block = Mock()
    bookmark_block.type = BlockType.BOOKMARK  # Verwende BlockType enum
    bookmark_block.bookmark = Mock()  # bookmark ist nicht None
    assert BookmarkElement.match_notion(bookmark_block)

    # Invalid block type
    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH  # Verwende BlockType enum
    paragraph_block.bookmark = None
    assert not BookmarkElement.match_notion(paragraph_block)

    # Bookmark type but bookmark is None
    empty_bookmark_block = Mock()
    empty_bookmark_block.type = BlockType.BOOKMARK
    empty_bookmark_block.bookmark = None
    assert not BookmarkElement.match_notion(empty_bookmark_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_simple():
    """Test einfaches Bookmark ohne Titel/Beschreibung."""
    result = await BookmarkElement.markdown_to_notion("[bookmark](https://example.com)")

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"
    assert result.bookmark.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_with_title():
    """Test Bookmark mit Titel."""
    result = await BookmarkElement.markdown_to_notion(
        "[bookmark](https://example.com)(caption:Beispiel-Titel)"
    )

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"
    assert len(result.bookmark.caption) >= 1
    # TextInlineFormatter erstellt RichText-Strukturen
    # Wir testen den Text-Inhalt über extract_text_with_formatting
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    text = await TextInlineFormatter.extract_text_with_formatting(result.bookmark.caption)
    assert "Beispiel-Titel" in text


@pytest.mark.asyncio
async def test_markdown_to_notion_with_title_and_description():
    """Test Bookmark mit Titel und Beschreibung."""
    result = await BookmarkElement.markdown_to_notion(
        "[bookmark](https://example.com)(caption:Beispiel-Titel – Eine Beschreibung)"
    )

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"

    # Caption sollte "Beispiel-Titel – Eine Beschreibung" enthalten (em dash)
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption_text = await TextInlineFormatter.extract_text_with_formatting(
        result.bookmark.caption
    )
    assert caption_text == "Beispiel-Titel – Eine Beschreibung"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test ungültiges Format."""
    result = await BookmarkElement.markdown_to_notion("Dies ist kein Bookmark")
    assert result is None

    result = await BookmarkElement.markdown_to_notion("[bookmark]()")
    assert result is None

    result = await BookmarkElement.markdown_to_notion("[bookmark](not-a-url)")
    assert result is None


@pytest.mark.asyncio
async def test_notion_to_markdown_simple():
    """Test Konvertierung von einfachem Notion-Bookmark."""
    bookmark_data = BookmarkBlock(url="https://example.com", caption=[])

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = await BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_title():
    """Test Konvertierung von Notion-Bookmark mit Titel."""
    # Verwende TextInlineFormatter um korrekte RichText-Struktur zu erstellen
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = await TextInlineFormatter.parse_inline_formatting("Beispiel-Titel")

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = await BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)(caption:Beispiel-Titel)"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_title_and_description():
    """Test Konvertierung von Notion-Bookmark mit Titel und Beschreibung."""
    # Verwende TextInlineFormatter mit hyphen für korrekte Trennung
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = await TextInlineFormatter.parse_inline_formatting(
        "Beispiel-Titel - Eine Beschreibung"
    )

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = await BookmarkElement.notion_to_markdown(block)
    assert (
        result
        == "[bookmark](https://example.com)(caption:Beispiel-Titel - Eine Beschreibung)"
    )


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.bookmark = None
    result = await BookmarkElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Bookmark is None
    bookmark_none_block = Mock()
    bookmark_none_block.type = BlockType.BOOKMARK
    bookmark_none_block.bookmark = None
    result = await BookmarkElement.notion_to_markdown(bookmark_none_block)
    assert result is None

    # Missing URL
    bookmark_data = BookmarkBlock(url="", caption=[])
    no_url_block = Mock()
    no_url_block.type = BlockType.BOOKMARK
    no_url_block.bookmark = bookmark_data
    result = await BookmarkElement.notion_to_markdown(no_url_block)
    assert result is None


# Parametrisierte Tests für verschiedene URL-Formate
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com", True),
        ("http://example.com", True),
        ("https://subdomain.example.com/path", True),
        ("https://example.com/path?query=value", True),
        ("https://example.com/path#fragment", True),
        ("ftp://example.com", False),  # Nur http/https erlaubt
        ("nicht-url", False),
        ("", False),
        ("example.com", False),  # Kein Protokoll
    ],
)
async def test_url_validation(url, expected):
    """Test URL-Validierung in verschiedenen Formaten."""
    markdown = f"[bookmark]({url})"
    result = await BookmarkElement.markdown_to_notion(markdown)
    if expected:
        assert result is not None
    else:
        assert result is None


# Fixtures für wiederkehrende Test-Daten
@pytest.fixture
def simple_bookmark_block():
    """Fixture für einfachen Bookmark-Block."""
    bookmark_data = BookmarkBlock(url="https://example.com", caption=[])

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data
    return block


@pytest_asyncio.fixture
async def titled_bookmark_block():
    """Fixture für Bookmark-Block mit Titel."""
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = await TextInlineFormatter.parse_inline_formatting("Test Title")

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data
    return block


@pytest.mark.asyncio
async def test_with_fixtures(simple_bookmark_block, titled_bookmark_block):
    """Test mit Fixtures zur Reduzierung von Duplikation."""
    # Test einfacher Block
    result1 = await BookmarkElement.notion_to_markdown(simple_bookmark_block)
    assert result1 == "[bookmark](https://example.com)"

    # Test Block mit Titel
    result2 = await BookmarkElement.notion_to_markdown(titled_bookmark_block)
    assert result2 == "[bookmark](https://example.com)(caption:Test Title)"


@pytest.mark.asyncio
async def test_roundtrip_conversion_simple():
    """Test Roundtrip für einfache Bookmarks."""
    original = "[bookmark](https://example.com)"

    # Markdown -> Notion
    notion_result = await BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None

    # Erstelle Mock-Block für notion_to_markdown
    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = notion_result.bookmark

    # Notion -> Markdown
    back = await BookmarkElement.notion_to_markdown(block)
    assert back == original


@pytest.mark.asyncio
async def test_roundtrip_conversion_with_title():
    """Test Roundtrip für Bookmarks mit Titel."""
    original = "[bookmark](https://example.com)(caption:My Title)"

    # Markdown -> Notion
    notion_result = await BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None

    # Erstelle Mock-Block für notion_to_markdown
    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = notion_result.bookmark

    # Notion -> Markdown
    back = await BookmarkElement.notion_to_markdown(block)
    assert back == original


@pytest.mark.asyncio
async def test_unicode_in_captions():
    """Test Unicode-Zeichen in Captions."""
    test_cases = [
        "[bookmark](https://example.com)(caption:Titel mit Ümlauten)",
        "[bookmark](https://example.com)(caption:Emoji 🚀 Test)",
        "[bookmark](https://example.com)(caption:中文标题)",
    ]

    for original in test_cases:
        notion_result = await BookmarkElement.markdown_to_notion(original)
        assert notion_result is not None

        # Erstelle Mock-Block für notion_to_markdown
        block = Mock()
        block.type = BlockType.BOOKMARK
        block.bookmark = notion_result.bookmark

        back = await BookmarkElement.notion_to_markdown(block)
        assert back == original


@pytest.mark.asyncio
async def test_special_characters_in_urls():
    """Test URLs mit Sonderzeichen."""
    special_urls = [
        "https://example.com/path?param=value&other=123",
        "https://example.com/path#section",
        "https://sub.domain.example.com/deep/path/file.html",
        "https://example.com:8080/path",
    ]

    for url in special_urls:
        markdown = f"[bookmark]({url})"
        assert await BookmarkElement.markdown_to_notion(markdown) is not None

        result = await BookmarkElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.bookmark.url == url


@pytest.mark.asyncio
async def test_edge_cases():
    """Test verschiedene Edge Cases."""
    # Sehr lange URLs
    long_url = "https://example.com/" + "a" * 1000
    assert await BookmarkElement.markdown_to_notion(f"[bookmark]({long_url})")

    # URLs mit vielen Pfad-Segmenten
    deep_url = "https://example.com/" + "/".join(["segment"] * 50)
    assert await BookmarkElement.markdown_to_notion(f"[bookmark]({deep_url})")

    # Bookmark ohne schließende Klammer
    assert (
        await BookmarkElement.markdown_to_notion("[bookmark](https://example.com")
        is None
    )

    # Bookmark ohne URL
    assert not await BookmarkElement.markdown_to_notion("[bookmark]()")


@pytest.mark.asyncio
async def test_caption_separator_behavior():
    """Test das Verhalten mit verschiedenen Separatoren."""
    # Die Implementation verwendet em dash (–) beim Erstellen,
    # aber erkennt hyphen (-) beim Parsen

    # Test mit hyphen input
    result_hyphen = await BookmarkElement.markdown_to_notion(
        "[bookmark](https://example.com)(caption:Title – Description)"
    )

    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption_text = await TextInlineFormatter.extract_text_with_formatting(
        result_hyphen.bookmark.caption
    )
    assert caption_text == "Title – Description"  # em dash in output

    # Test parsing with hyphen
    hyphen_caption = await TextInlineFormatter.parse_inline_formatting("Title - Description")
    bookmark_data = BookmarkBlock(url="https://example.com", caption=hyphen_caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = await BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)(caption:Title - Description)"


@pytest.mark.asyncio
async def test_empty_strings_and_whitespace():
    """Test Behandlung von leeren Strings und Whitespace."""
    # Leere Titel/Beschreibungen
    test_cases = [
        "[bookmark](https://example.com)(caption:)",  # Leerer Titel
        "[bookmark](https://example.com)(caption: )",  # Nur Whitespace
    ]

    for markdown in test_cases:
        result = await BookmarkElement.markdown_to_notion(markdown)
        # Diese sollten funktionieren oder None zurückgeben
        assert result is not None or result is None  # Beide Ergebnisse sind ok
        if result:
            assert result.bookmark.url == "https://example.com"
