"""
Pytest tests for BulletedListElement.
Clean and simple tests without unittest boilerplate.
"""

import pytest
from notionary.blocks import BulletedListElement


def test_match_markdown_valid_bullets():
    """Test gültige Bullet-Formate."""
    assert BulletedListElement.match_markdown("- Bullet item")
    assert BulletedListElement.match_markdown("* Another bullet")
    assert BulletedListElement.match_markdown("+ Yet another bullet")


def test_match_markdown_invalid_formats():
    """Test ungültige Formate (Todo-Items und normaler Text)."""
    assert not BulletedListElement.match_markdown("- [ ] Todo item")
    assert not BulletedListElement.match_markdown("- [x] Done todo")
    assert not BulletedListElement.match_markdown("Regular text")
    assert not BulletedListElement.match_markdown("1. Numbered item")


def test_match_notion():
    """Test die Erkennung von Notion-Bulleted-List-Blöcken."""
    assert BulletedListElement.match_notion({"type": "bulleted_list_item"})
    
    assert not BulletedListElement.match_notion({"type": "paragraph"})
    assert not BulletedListElement.match_notion({"type": "numbered_list_item"})
    assert not BulletedListElement.match_notion({"type": "to_do"})


def test_markdown_to_notion():
    """Test Konvertierung von Markdown zu Notion-Block."""
    result = BulletedListElement.markdown_to_notion("- A bullet item")
    
    assert result is not None
    assert result["type"] == "bulleted_list_item"
    assert result["bulleted_list_item"]["color"] == "default"
    assert result["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "A bullet item"


def test_markdown_to_notion_with_formatting():
    """Test Markdown mit Inline-Formatierung."""
    result = BulletedListElement.markdown_to_notion("- **Bold** and *italic* text")
    
    assert result is not None
    assert result["type"] == "bulleted_list_item"
    # rich_text sollte mehrere Segmente für Formatierung enthalten
    assert len(result["bulleted_list_item"]["rich_text"]) > 1


def test_markdown_to_notion_invalid():
    """Test ungültiges Markdown."""
    result = BulletedListElement.markdown_to_notion("Regular text")
    assert result is None
    
    result = BulletedListElement.markdown_to_notion("- [ ] Todo item")
    assert result is None


def test_notion_to_markdown():
    """Test Konvertierung von Notion-Block zu Markdown."""
    block = {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "List entry"}}],
            "color": "default",
        },
    }
    
    result = BulletedListElement.notion_to_markdown(block)
    assert result == "- List entry"


def test_notion_to_markdown_with_formatting():
    """Test Notion-Block mit Rich-Text-Formatierung."""
    block = {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Bold"},
                    "annotations": {"bold": True},
                },
                {
                    "type": "text", 
                    "text": {"content": " and "},
                    "annotations": {"bold": False},
                },
                {
                    "type": "text",
                    "text": {"content": "italic"},
                    "annotations": {"italic": True},
                }
            ],
            "color": "default",
        },
    }
    
    result = BulletedListElement.notion_to_markdown(block)
    assert "**Bold**" in result
    assert "*italic*" in result


def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    result = BulletedListElement.notion_to_markdown({"type": "paragraph"})
    assert result is None


def test_is_multiline():
    """Test dass Bullet-Items als einzeilige Elemente erkannt werden."""
    assert not BulletedListElement.is_multiline()


# Parametrisierte Tests für verschiedene Bullet-Marker
@pytest.mark.parametrize("marker,text,expected", [
    ("-", "Item text", True),
    ("*", "Item text", True), 
    ("+", "Item text", True),
    ("", "Item text", False),
    ("1.", "Item text", False),
])
def test_bullet_markers(marker, text, expected):
    """Test verschiedene Bullet-Marker."""
    if marker:
        markdown = f"{marker} {text}"
    else:
        markdown = text
        
    result = BulletedListElement.match_markdown(markdown)
    assert result == expected


@pytest.mark.parametrize("markdown,should_match", [
    ("- Simple item", True),
    ("  - Indented item", True),
    ("* Asterisk item", True),
    ("+ Plus item", True),
    ("- [ ] Todo item", False),
    ("- [x] Done todo", False),
    ("1. Numbered item", False),
    ("Regular text", False),
    ("", False),
])
def test_markdown_patterns(markdown, should_match):
    """Test verschiedene Markdown-Patterns."""
    result = BulletedListElement.match_markdown(markdown)
    assert result == should_match


# Fixtures für wiederkehrende Test-Daten
@pytest.fixture
def simple_bullet_block():
    """Fixture für einfachen Bullet-Block."""
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Test item"}}],
            "color": "default",
        },
    }


@pytest.fixture
def formatted_bullet_block():
    """Fixture für Bullet-Block mit Formatierung."""
    return {
        "type": "bulleted_list_item", 
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Bold text"},
                    "annotations": {"bold": True},
                }
            ],
            "color": "default",
        },
    }


def test_with_fixtures(simple_bullet_block, formatted_bullet_block):
    """Test mit Fixtures zur Reduzierung von Duplikation."""
    # Test einfacher Block
    result1 = BulletedListElement.notion_to_markdown(simple_bullet_block)
    assert result1 == "- Test item"
    
    # Test formatierter Block 
    result2 = BulletedListElement.notion_to_markdown(formatted_bullet_block)
    assert "**Bold text**" in result2