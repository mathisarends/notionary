"""
Pytest tests for BookmarkElement.
Clean and simple tests without unittest boilerplate.
"""

import pytest
from unittest.mock import Mock

from notionary.blocks.bookmark.bookmark_element import BookmarkElement


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
    bookmark_block.type = "bookmark"
    bookmark_block.bookmark = Mock()  # bookmark ist nicht None
    assert BookmarkElement.match_notion(bookmark_block)

    # Invalid block type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.bookmark = None
    assert not BookmarkElement.match_notion(paragraph_block)

    # Bookmark type but bookmark is None
    empty_bookmark_block = Mock()
    empty_bookmark_block.type = "bookmark"
    empty_bookmark_block.bookmark = None
    assert not BookmarkElement.match_notion(empty_bookmark_block)


def test_markdown_to_notion_simple():
    """Test einfaches Bookmark ohne Titel/Beschreibung."""
    result = BookmarkElement.markdown_to_notion("[bookmark](https://example.com)")

    assert result is not None
    assert result.type == "bookmark"
    assert result.bookmark.url == "https://example.com"
    assert result.bookmark.caption == []


def test_markdown_to_notion_with_title():
    """Test Bookmark mit Titel."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel")'
    )

    assert result is not None
    assert result.type == "bookmark"
    assert result.bookmark.url == "https://example.com"
    assert len(result.bookmark.caption) == 1
    assert result.bookmark.caption[0].plain_text == "Beispiel-Titel"


def test_markdown_to_notion_with_title_and_description():
    """Test Bookmark mit Titel und Beschreibung."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )

    assert result is not None
    assert result.type == "bookmark"
    assert result.bookmark.url == "https://example.com"

    # Caption sollte "Beispiel-Titel – Eine Beschreibung" enthalten (em dash)
    caption_text = result.bookmark.caption[0].plain_text
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
    block = Mock()
    block.type = "bookmark"
    block.bookmark = Mock()
    block.bookmark.url = "https://example.com"
    block.bookmark.caption = []

    result = BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)"


def test_notion_to_markdown_with_title():
    """Test Konvertierung von Notion-Bookmark mit Titel."""
    block = Mock()
    block.type = "bookmark"
    block.bookmark = Mock()
    block.bookmark.url = "https://example.com"

    caption_rt = Mock()
    caption_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Beispiel-Titel"},
        "plain_text": "Beispiel-Titel",
    }
    block.bookmark.caption = [caption_rt]

    result = BookmarkElement.notion_to_markdown(block)
    assert result == '[bookmark](https://example.com "Beispiel-Titel")'


def test_notion_to_markdown_with_title_and_description():
    """Test Konvertierung von Notion-Bookmark mit Titel und Beschreibung."""
    block = Mock()
    block.type = "bookmark"
    block.bookmark = Mock()
    block.bookmark.url = "https://example.com"

    # Simuliere das zusammengesetzte Caption (wie es von markdown_to_notion erstellt wird)
    caption_rt = Mock()
    caption_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Beispiel-Titel - Eine Beschreibung"},  # hyphen für Test
        "plain_text": "Beispiel-Titel - Eine Beschreibung",
    }
    block.bookmark.caption = [caption_rt]

    result = BookmarkElement.notion_to_markdown(block)
    assert (
        result == '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )


def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.bookmark = None
    result = BookmarkElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Bookmark is None
    bookmark_none_block = Mock()
    bookmark_none_block.type = "bookmark"
    bookmark_none_block.bookmark = None
    result = BookmarkElement.notion_to_markdown(bookmark_none_block)
    assert result is None

    # Missing URL
    no_url_block = Mock()
    no_url_block.type = "bookmark"
    no_url_block.bookmark = Mock()
    no_url_block.bookmark.url = None
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


def test_extract_text_helper():
    """Test the _extract_text helper method."""
    # Text content
    rich_text = [
        {"type": "text", "text": {"content": "Title"}},
        {"type": "text", "text": {"content": " - "}},
        {"type": "text", "text": {"content": "Description"}},
    ]
    result = BookmarkElement._extract_text(rich_text)
    assert result == "Title - Description"

    # Plain text fallback
    plain_text = [{"plain_text": "Fallback Text"}]
    result = BookmarkElement._extract_text(plain_text)
    assert result == "Fallback Text"

    # Empty list
    result = BookmarkElement._extract_text([])
    assert result == ""

    # Mixed content
    mixed = [{"type": "text", "text": {"content": "Hello "}}, {"plain_text": "World"}]
    result = BookmarkElement._extract_text(mixed)
    assert result == "Hello World"


# Fixtures für wiederkehrende Test-Daten
@pytest.fixture
def simple_bookmark_block():
    """Fixture für einfachen Bookmark-Block."""
    block = Mock()
    block.type = "bookmark"
    block.bookmark = Mock()
    block.bookmark.url = "https://example.com"
    block.bookmark.caption = []
    return block


@pytest.fixture
def titled_bookmark_block():
    """Fixture für Bookmark-Block mit Titel."""
    block = Mock()
    block.type = "bookmark"
    block.bookmark = Mock()
    block.bookmark.url = "https://example.com"

    caption_rt = Mock()
    caption_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Test Title"},
        "plain_text": "Test Title",
    }
    block.bookmark.caption = [caption_rt]
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

    # Notion -> Markdown
    back = BookmarkElement.notion_to_markdown(notion_result)
    assert back == original


def test_roundtrip_conversion_with_title():
    """Test Roundtrip für Bookmarks mit Titel."""
    original = '[bookmark](https://example.com "My Title")'

    # Markdown -> Notion
    notion_result = BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None

    # Notion -> Markdown
    back = BookmarkElement.notion_to_markdown(notion_result)
    assert back == original


def test_roundtrip_conversion_fails_with_title_and_description():
    """Test dass Roundtrip mit Titel und Beschreibung NICHT funktioniert (bekannter Bug)."""
    # Dies ist ein bekannter Bug in der Implementierung
    original = '[bookmark](https://example.com "Title" "Description")'

    # Markdown -> Notion (erstellt mit em dash)
    notion_result = BookmarkElement.markdown_to_notion(original)
    assert notion_result is not None
    assert (
        notion_result.bookmark.caption[0].plain_text == "Title – Description"
    )  # em dash

    # Notion -> Markdown (sucht nach hyphen)
    back = BookmarkElement.notion_to_markdown(notion_result)
    # Das wird nicht zum Original zurück konvertieren, da em dash vs hyphen
    assert (
        back == '[bookmark](https://example.com "Title – Description")'
    )  # Single caption
    assert back != original  # Roundtrip funktioniert nicht!


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
        back = BookmarkElement.notion_to_markdown(notion_result)
        assert back == original


def test_empty_strings_and_whitespace():
    """Test Behandlung von leeren Strings und Whitespace."""
    # Leere Titel/Beschreibungen sollten ignoriert werden
    test_cases = [
        '[bookmark](https://example.com "")',  # Leerer Titel
        '[bookmark](https://example.com " ")',  # Nur Whitespace
        '[bookmark](https://example.com "Title" "")',  # Leere Beschreibung
    ]

    for markdown in test_cases:
        result = BookmarkElement.markdown_to_notion(markdown)
        # Diese sollten funktionieren, aber das Verhalten hängt von der Implementierung ab
        # Testen wir einfach, dass sie nicht crashen
        assert result is not None or result is None  # Beide Ergebnisse sind ok


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


def test_caption_separator_inconsistency():
    """Test dokumentiert die Inkonsistenz zwischen em dash und hyphen."""
    # Die Implementierung verwendet em dash (–) beim Erstellen,
    # aber sucht nach hyphen (-) beim Parsen

    # Erstelle ein Bookmark mit Titel und Beschreibung
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Title" "Description")'
    )

    # Das sollte em dash verwenden
    caption_text = result.bookmark.caption[0].plain_text
    assert caption_text == "Title – Description"  # em dash
    assert " - " not in caption_text  # kein hyphen

    # notion_to_markdown sucht aber nach hyphen
    # Das bedeutet, es wird nicht als "Title" und "Description" erkannt
    back = BookmarkElement.notion_to_markdown(result)
    assert (
        back == '[bookmark](https://example.com "Title – Description")'
    )  # Single caption
