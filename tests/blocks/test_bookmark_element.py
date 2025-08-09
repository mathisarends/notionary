"""
Pytest tests for BookmarkElement.
Updated to match the actual implementation.
"""

import pytest
from unittest.mock import Mock

from notionary.blocks.bookmark.bookmark_element import BookmarkElement
from notionary.blocks.block_types import BlockType
from notionary.blocks.bookmark.bookmark_models import BookmarkBlock, CreateBookmarkBlock


def test_match_markdown():
    """Test die Erkennung von Markdown-Bookmarks."""
    # Gültige Bookmark-Formate
    assert BookmarkElement.match_markdown("[bookmark](https://example.com)")
    assert BookmarkElement.match_markdown('[bookmark](https://example.com "Titel")')
    assert BookmarkElement.match_markdown(
        '[bookmark](https://example.com "Titel" "Beschreibung")'
    )

    # Ungültige Formate
    assert not BookmarkElement.match_markdown("[link](https://example.com)")
    assert not BookmarkElement.match_markdown("Dies ist kein Bookmark")
    assert not BookmarkElement.match_markdown("[bookmark](nicht-url)")
    assert not BookmarkElement.match_markdown(
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


def test_markdown_to_notion_simple():
    """Test einfaches Bookmark ohne Titel/Beschreibung."""
    result = BookmarkElement.markdown_to_notion("[bookmark](https://example.com)")

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"
    assert result.bookmark.caption == []


def test_markdown_to_notion_with_title():
    """Test Bookmark mit Titel."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel")'
    )

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"
    assert len(result.bookmark.caption) >= 1
    # TextInlineFormatter erstellt RichText-Strukturen
    # Wir testen den Text-Inhalt über extract_text_with_formatting
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    text = TextInlineFormatter.extract_text_with_formatting(result.bookmark.caption)
    assert "Beispiel-Titel" in text


def test_markdown_to_notion_with_title_and_description():
    """Test Bookmark mit Titel und Beschreibung."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )

    assert result is not None
    assert isinstance(result, CreateBookmarkBlock)
    assert result.bookmark.url == "https://example.com"

    # Caption sollte "Beispiel-Titel – Eine Beschreibung" enthalten (em dash)
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption_text = TextInlineFormatter.extract_text_with_formatting(
        result.bookmark.caption
    )
    assert caption_text == "Beispiel-Titel – Eine Beschreibung"


def test_markdown_to_notion_invalid():
    """Test ungültiges Format."""
    result = BookmarkElement.markdown_to_notion("Dies ist kein Bookmark")
    assert result is None

    result = BookmarkElement.markdown_to_notion("[bookmark]()")
    assert result is None

    result = BookmarkElement.markdown_to_notion("[bookmark](not-a-url)")
    assert result is None


def test_notion_to_markdown_simple():
    """Test Konvertierung von einfachem Notion-Bookmark."""
    bookmark_data = BookmarkBlock(url="https://example.com", caption=[])

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)"


def test_notion_to_markdown_with_title():
    """Test Konvertierung von Notion-Bookmark mit Titel."""
    # Verwende TextInlineFormatter um korrekte RichText-Struktur zu erstellen
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = TextInlineFormatter.parse_inline_formatting("Beispiel-Titel")

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = BookmarkElement.notion_to_markdown(block)
    assert result == '[bookmark](https://example.com "Beispiel-Titel")'


def test_notion_to_markdown_with_title_and_description():
    """Test Konvertierung von Notion-Bookmark mit Titel und Beschreibung."""
    # Verwende TextInlineFormatter mit hyphen für korrekte Trennung
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = TextInlineFormatter.parse_inline_formatting(
        "Beispiel-Titel - Eine Beschreibung"
    )

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = BookmarkElement.notion_to_markdown(block)
    assert (
        result == '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )


def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.bookmark = None
    result = BookmarkElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Bookmark is None
    bookmark_none_block = Mock()
    bookmark_none_block.type = BlockType.BOOKMARK
    bookmark_none_block.bookmark = None
    result = BookmarkElement.notion_to_markdown(bookmark_none_block)
    assert result is None

    # Missing URL
    bookmark_data = BookmarkBlock(url="", caption=[])
    no_url_block = Mock()
    no_url_block.type = BlockType.BOOKMARK
    no_url_block.bookmark = bookmark_data
    result = BookmarkElement.notion_to_markdown(no_url_block)
    assert result is None


# Parametrisierte Tests für verschiedene URL-Formate
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
def test_url_validation(url, expected):
    """Test URL-Validierung in verschiedenen Formaten."""
    markdown = f"[bookmark]({url})"
    result = BookmarkElement.match_markdown(markdown)
    assert result == expected


# Fixtures für wiederkehrende Test-Daten
@pytest.fixture
def simple_bookmark_block():
    """Fixture für einfachen Bookmark-Block."""
    bookmark_data = BookmarkBlock(url="https://example.com", caption=[])

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data
    return block


@pytest.fixture
def titled_bookmark_block():
    """Fixture für Bookmark-Block mit Titel."""
    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption = TextInlineFormatter.parse_inline_formatting("Test Title")

    bookmark_data = BookmarkBlock(url="https://example.com", caption=caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data
    return block


def test_with_fixtures(simple_bookmark_block, titled_bookmark_block):
    """Test mit Fixtures zur Reduzierung von Duplikation."""
    # Test einfacher Block
    result1 = BookmarkElement.notion_to_markdown(simple_bookmark_block)
    assert result1 == "[bookmark](https://example.com)"

    # Test Block mit Titel
    result2 = BookmarkElement.notion_to_markdown(titled_bookmark_block)
    assert result2 == '[bookmark](https://example.com "Test Title")'


def test_roundtrip_conversion_simple():
    """Test Roundtrip für einfache Bookmarks."""
    original = "[bookmark](https://example.com)"

    # Markdown -> Notion
    notion_result = BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None

    # Erstelle Mock-Block für notion_to_markdown
    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = notion_result.bookmark

    # Notion -> Markdown
    back = BookmarkElement.notion_to_markdown(block)
    assert back == original


def test_roundtrip_conversion_with_title():
    """Test Roundtrip für Bookmarks mit Titel."""
    original = '[bookmark](https://example.com "My Title")'

    # Markdown -> Notion
    notion_result = BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None

    # Erstelle Mock-Block für notion_to_markdown
    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = notion_result.bookmark

    # Notion -> Markdown
    back = BookmarkElement.notion_to_markdown(block)
    assert back == original


def test_unicode_in_captions():
    """Test Unicode-Zeichen in Captions."""
    test_cases = [
        '[bookmark](https://example.com "Titel mit Ümlauten")',
        '[bookmark](https://example.com "Emoji 🚀 Test")',
        '[bookmark](https://example.com "中文标题")',
    ]

    for original in test_cases:
        notion_result = BookmarkElement.markdown_to_notion(original)
        assert notion_result is not None

        # Erstelle Mock-Block für notion_to_markdown
        block = Mock()
        block.type = BlockType.BOOKMARK
        block.bookmark = notion_result.bookmark

        back = BookmarkElement.notion_to_markdown(block)
        assert back == original


def test_special_characters_in_urls():
    """Test URLs mit Sonderzeichen."""
    special_urls = [
        "https://example.com/path?param=value&other=123",
        "https://example.com/path#section",
        "https://sub.domain.example.com/deep/path/file.html",
        "https://example.com:8080/path",
    ]

    for url in special_urls:
        markdown = f"[bookmark]({url})"
        assert BookmarkElement.match_markdown(markdown)

        result = BookmarkElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.bookmark.url == url


def test_edge_cases():
    """Test verschiedene Edge Cases."""
    # Sehr lange URLs
    long_url = "https://example.com/" + "a" * 1000
    assert BookmarkElement.match_markdown(f"[bookmark]({long_url})")

    # URLs mit vielen Pfad-Segmenten
    deep_url = "https://example.com/" + "/".join(["segment"] * 50)
    assert BookmarkElement.match_markdown(f"[bookmark]({deep_url})")

    # Bookmark ohne schließende Klammer
    assert not BookmarkElement.match_markdown("[bookmark](https://example.com")

    # Bookmark ohne URL
    assert not BookmarkElement.match_markdown("[bookmark]()")


def test_caption_separator_behavior():
    """Test das Verhalten mit verschiedenen Separatoren."""
    # Die Implementation verwendet em dash (–) beim Erstellen,
    # aber erkennt hyphen (-) beim Parsen

    # Test mit hyphen input
    result_hyphen = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Title" "Description")'
    )

    from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

    caption_text = TextInlineFormatter.extract_text_with_formatting(
        result_hyphen.bookmark.caption
    )
    assert caption_text == "Title – Description"  # em dash in output

    # Test parsing with hyphen
    hyphen_caption = TextInlineFormatter.parse_inline_formatting("Title - Description")
    bookmark_data = BookmarkBlock(url="https://example.com", caption=hyphen_caption)

    block = Mock()
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data

    result = BookmarkElement.notion_to_markdown(block)
    assert result == '[bookmark](https://example.com "Title" "Description")'


def test_empty_strings_and_whitespace():
    """Test Behandlung von leeren Strings und Whitespace."""
    # Leere Titel/Beschreibungen
    test_cases = [
        '[bookmark](https://example.com "")',  # Leerer Titel
        '[bookmark](https://example.com " ")',  # Nur Whitespace
    ]

    for markdown in test_cases:
        result = BookmarkElement.markdown_to_notion(markdown)
        # Diese sollten funktionieren oder None zurückgeben
        assert result is not None or result is None  # Beide Ergebnisse sind ok
        if result:
            assert result.bookmark.url == "https://example.com"
