"""
Pytest tests for BookmarkElement.
Clean and simple tests without unittest boilerplate.
"""

import pytest
from notionary.blocks import BookmarkElement


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


def test_match_notion():
    """Test die Erkennung von Notion-Bookmark-Blöcken."""
    assert BookmarkElement.match_notion(
        {"type": "bookmark", "bookmark": {"url": "https://example.com"}}
    )

    assert not BookmarkElement.match_notion({"type": "paragraph"})
    assert not BookmarkElement.match_notion(
        {"bookmark": {"url": "https://example.com"}}
    )


def test_markdown_to_notion_simple():
    """Test einfaches Bookmark ohne Titel/Beschreibung."""
    result = BookmarkElement.markdown_to_notion("[bookmark](https://example.com)")

    assert result[0]["type"] == "bookmark"
    assert result[0]["bookmark"]["url"] == "https://example.com"
    assert result[0]["bookmark"]["caption"] == []


def test_markdown_to_notion_with_title():
    """Test Bookmark mit Titel."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel")'
    )

    assert result[0]["type"] == "bookmark"
    assert result[0]["bookmark"]["url"] == "https://example.com"
    assert result[0]["bookmark"]["caption"][0]["text"]["content"] == "Beispiel-Titel"


def test_markdown_to_notion_with_title_and_description():
    """Test Bookmark mit Titel und Beschreibung."""
    result = BookmarkElement.markdown_to_notion(
        '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )

    assert result[0]["type"] == "bookmark"
    assert result[0]["bookmark"]["url"] == "https://example.com"

    # Caption sollte "Beispiel-Titel - Eine Beschreibung" enthalten
    caption_text = result[0]["bookmark"]["caption"][0]["text"]["content"]
    assert caption_text == "Beispiel-Titel - Eine Beschreibung"


def test_markdown_to_notion_invalid():
    """Test ungültiges Format."""
    result = BookmarkElement.markdown_to_notion("Dies ist kein Bookmark")
    assert result is None


def test_notion_to_markdown_simple():
    """Test Konvertierung von einfachem Notion-Bookmark."""
    block = {"type": "bookmark", "bookmark": {"url": "https://example.com"}}

    result = BookmarkElement.notion_to_markdown(block)
    assert result == "[bookmark](https://example.com)"


def test_notion_to_markdown_with_title():
    """Test Konvertierung von Notion-Bookmark mit Titel."""
    block = {
        "type": "bookmark",
        "bookmark": {
            "url": "https://example.com",
            "caption": [{"type": "text", "text": {"content": "Beispiel-Titel"}}],
        },
    }

    result = BookmarkElement.notion_to_markdown(block)
    assert result == '[bookmark](https://example.com "Beispiel-Titel")'


def test_notion_to_markdown_with_title_and_description():
    """Test Konvertierung von Notion-Bookmark mit Titel und Beschreibung."""
    block = {
        "type": "bookmark",
        "bookmark": {
            "url": "https://example.com",
            "caption": [
                {"type": "text", "text": {"content": "Beispiel-Titel"}},
                {"type": "text", "text": {"content": " - "}},
                {"type": "text", "text": {"content": "Eine Beschreibung"}},
            ],
        },
    }

    result = BookmarkElement.notion_to_markdown(block)
    assert (
        result == '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
    )


def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    result = BookmarkElement.notion_to_markdown({"type": "paragraph"})
    assert result is None


def test_is_multiline():
    """Test, dass Bookmarks als einzeilige Elemente erkannt werden."""
    assert not BookmarkElement.is_multiline()


# Parametrisierte Tests für verschiedene URL-Formate
@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com", True),
        ("http://example.com", True),
        ("https://subdomain.example.com/path", True),
        (
            "ftp://example.com",
            False,
        ),  # Sollte false sein, da regex nur http/https akzeptiert
        ("nicht-url", False),
        ("", False),
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
    return {"type": "bookmark", "bookmark": {"url": "https://example.com"}}


@pytest.fixture
def titled_bookmark_block():
    """Fixture für Bookmark-Block mit Titel."""
    return {
        "type": "bookmark",
        "bookmark": {
            "url": "https://example.com",
            "caption": [{"type": "text", "text": {"content": "Test Title"}}],
        },
    }


def test_with_fixtures(simple_bookmark_block, titled_bookmark_block):
    """Test mit Fixtures zur Reduzierung von Duplikation."""
    # Test einfacher Block
    result1 = BookmarkElement.notion_to_markdown(simple_bookmark_block)
    assert result1 == "[bookmark](https://example.com)"

    # Test Block mit Titel
    result2 = BookmarkElement.notion_to_markdown(titled_bookmark_block)
    assert result2 == '[bookmark](https://example.com "Test Title")'
