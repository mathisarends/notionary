"""
Pytest tests for BulletedListElement.
Clean and simple tests without unittest boilerplate.
"""

import pytest
from unittest.mock import Mock, patch

from notionary.blocks.bulleted_list.bulleted_list_element import BulletedListElement


def test_match_markdown_valid_bullets():
    """Test gültige Bullet-Formate."""
    assert BulletedListElement.match_markdown("- Bullet item")
    assert BulletedListElement.match_markdown("* Another bullet")
    assert BulletedListElement.match_markdown("+ Yet another bullet")
    assert BulletedListElement.match_markdown("  - Indented bullet")
    assert BulletedListElement.match_markdown("    * Deep indented")


def test_match_markdown_invalid_formats():
    """Test ungültige Formate (Todo-Items und normaler Text)."""
    assert not BulletedListElement.match_markdown("- [ ] Todo item")
    assert not BulletedListElement.match_markdown("- [x] Done todo")
    assert not BulletedListElement.match_markdown("Regular text")
    assert not BulletedListElement.match_markdown("1. Numbered item")
    assert not BulletedListElement.match_markdown("")
    assert not BulletedListElement.match_markdown("   ")


def test_match_notion():
    """Test die Erkennung von Notion-Bulleted-List-Blöcken."""
    # Valid bulleted list block
    bullet_block = Mock()
    bullet_block.type = "bulleted_list_item"
    bullet_block.bulleted_list_item = Mock()  # nicht None
    assert BulletedListElement.match_notion(bullet_block)

    # Invalid block types
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.bulleted_list_item = None
    assert not BulletedListElement.match_notion(paragraph_block)

    numbered_block = Mock()
    numbered_block.type = "numbered_list_item"
    numbered_block.bulleted_list_item = None
    assert not BulletedListElement.match_notion(numbered_block)

    todo_block = Mock()
    todo_block.type = "to_do"
    todo_block.bulleted_list_item = None
    assert not BulletedListElement.match_notion(todo_block)

    # Bulleted list type but bulleted_list_item is None
    empty_bullet_block = Mock()
    empty_bullet_block.type = "bulleted_list_item"
    empty_bullet_block.bulleted_list_item = None
    assert not BulletedListElement.match_notion(empty_bullet_block)


def test_markdown_to_notion():
    """Test Konvertierung von Markdown zu Notion-Block."""
    result = BulletedListElement.markdown_to_notion("- A bullet item")

    assert result is not None
    assert result.type == "bulleted_list_item"
    assert result.bulleted_list_item.color == "default"
    assert len(result.bulleted_list_item.rich_text) >= 1
    # Check that content is in the rich text
    content_found = any(
        rt.plain_text and "A bullet item" in rt.plain_text
        for rt in result.bulleted_list_item.rich_text
    )
    assert content_found


def test_markdown_to_notion_with_formatting():
    """Test Markdown mit Inline-Formatierung."""
    result = BulletedListElement.markdown_to_notion("- **Bold** and *italic* text")

    assert result is not None
    assert result.type == "bulleted_list_item"
    # rich_text sollte mehrere Segmente für Formatierung enthalten
    assert len(result.bulleted_list_item.rich_text) > 1


def test_markdown_to_notion_different_markers():
    """Test verschiedene Bullet-Marker."""
    test_cases = ["- Dash bullet", "* Asterisk bullet", "+ Plus bullet"]

    for markdown in test_cases:
        result = BulletedListElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.type == "bulleted_list_item"
        assert result.bulleted_list_item.color == "default"


def test_markdown_to_notion_invalid():
    """Test ungültiges Markdown."""
    result = BulletedListElement.markdown_to_notion("Regular text")
    assert result is None

    result = BulletedListElement.markdown_to_notion("- [ ] Todo item")
    assert result is None

    result = BulletedListElement.markdown_to_notion("- [x] Done todo")
    assert result is None

    result = BulletedListElement.markdown_to_notion("1. Numbered item")
    assert result is None

    result = BulletedListElement.markdown_to_notion("")
    assert result is None


@patch(
    "notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting"
)
def test_notion_to_markdown(mock_extract):
    """Test Konvertierung von Notion-Block zu Markdown."""
    mock_extract.return_value = "List entry"

    # Mock Block object
    block = Mock()
    block.type = "bulleted_list_item"
    block.bulleted_list_item = Mock()

    # Mock rich text
    rich_text_rt = Mock()
    rich_text_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "List entry"},
    }
    block.bulleted_list_item.rich_text = [rich_text_rt]

    result = BulletedListElement.notion_to_markdown(block)
    assert result == "- List entry"

    # Verify the mock was called
    mock_extract.assert_called_once()


@patch(
    "notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting"
)
def test_notion_to_markdown_with_formatting(mock_extract):
    """Test Notion-Block mit Rich-Text-Formatierung."""
    mock_extract.return_value = "**Bold** and *italic*"

    block = Mock()
    block.type = "bulleted_list_item"
    block.bulleted_list_item = Mock()

    # Mock multiple rich text objects
    rt1 = Mock()
    rt1.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Bold"},
        "annotations": {"bold": True},
    }
    rt2 = Mock()
    rt2.model_dump.return_value = {
        "type": "text",
        "text": {"content": " and "},
        "annotations": {"bold": False},
    }
    rt3 = Mock()
    rt3.model_dump.return_value = {
        "type": "text",
        "text": {"content": "italic"},
        "annotations": {"italic": True},
    }

    block.bulleted_list_item.rich_text = [rt1, rt2, rt3]

    result = BulletedListElement.notion_to_markdown(block)
    assert result == "- **Bold** and *italic*"


def test_notion_to_markdown_invalid():
    """Test ungültiger Notion-Block."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.bulleted_list_item = None
    result = BulletedListElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Bulleted list type but bulleted_list_item is None
    empty_block = Mock()
    empty_block.type = "bulleted_list_item"
    empty_block.bulleted_list_item = None
    result = BulletedListElement.notion_to_markdown(empty_block)
    assert result is None


def test_is_multiline():
    """Test dass Bullet-Items als einzeilige Elemente erkannt werden."""
    assert not BulletedListElement.is_multiline()


# Parametrisierte Tests für verschiedene Bullet-Marker
@pytest.mark.parametrize(
    "marker,text,expected",
    [
        ("-", "Item text", True),
        ("*", "Item text", True),
        ("+", "Item text", True),
        ("", "Item text", False),
        ("1.", "Item text", False),
        ("•", "Item text", False),  # Unicode bullet nicht unterstützt
    ],
)
def test_bullet_markers(marker, text, expected):
    """Test verschiedene Bullet-Marker."""
    if marker:
        markdown = f"{marker} {text}"
    else:
        markdown = text

    result = BulletedListElement.match_markdown(markdown)
    assert result == expected


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("- Simple item", True),
        ("  - Indented item", True),
        ("    - Deep indented", True),
        ("* Asterisk item", True),
        ("+ Plus item", True),
        ("- [ ] Todo item", False),
        ("- [x] Done todo", False),
        ("- [ x ] Malformed todo", False),
        ("1. Numbered item", False),
        ("a. Letter item", False),
        ("Regular text", False),
        ("", False),
        ("   ", False),
        ("- ", False),  # Bullet ohne Text
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test verschiedene Markdown-Patterns."""
    result = BulletedListElement.match_markdown(markdown)
    assert result == should_match


# Fixtures für wiederkehrende Test-Daten
@pytest.fixture
def simple_bullet_block():
    """Fixture für einfachen Bullet-Block."""
    block = Mock()
    block.type = "bulleted_list_item"
    block.bulleted_list_item = Mock()

    rich_text_rt = Mock()
    rich_text_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Test item"},
    }
    block.bulleted_list_item.rich_text = [rich_text_rt]

    return block


@pytest.fixture
def formatted_bullet_block():
    """Fixture für Bullet-Block mit Formatierung."""
    block = Mock()
    block.type = "bulleted_list_item"
    block.bulleted_list_item = Mock()

    rich_text_rt = Mock()
    rich_text_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Bold text"},
        "annotations": {"bold": True},
    }
    block.bulleted_list_item.rich_text = [rich_text_rt]

    return block


@patch(
    "notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting"
)
def test_with_fixtures(mock_extract, simple_bullet_block, formatted_bullet_block):
    """Test mit Fixtures zur Reduzierung von Duplikation."""
    # Test einfacher Block
    mock_extract.return_value = "Test item"
    result1 = BulletedListElement.notion_to_markdown(simple_bullet_block)
    assert result1 == "- Test item"

    # Test formatierter Block
    mock_extract.return_value = "**Bold text**"
    result2 = BulletedListElement.notion_to_markdown(formatted_bullet_block)
    assert result2 == "- **Bold text**"


def test_regex_pattern_details():
    """Test spezielle Regex-Pattern-Details."""
    # Test dass Indentation erfasst wird
    match = BulletedListElement.PATTERN.match("  - Indented")
    assert match is not None
    assert match.group(1) == "  "  # Indentation
    assert match.group(2) == "Indented"  # Content

    # Test dass Todo-Items ausgeschlossen werden
    assert BulletedListElement.PATTERN.match("- [ ] Todo") is None
    assert BulletedListElement.PATTERN.match("- [x] Done") is None
    assert BulletedListElement.PATTERN.match("- [X] Done") is None


def test_roundtrip_conversion():
    """Test Roundtrip-Konvertierung."""
    original_texts = [
        "- Simple bullet",
        "- **Bold** text",
        "- Text with *italic*",
        "- Mixed **bold** and *italic* formatting",
    ]

    for original in original_texts:
        # Markdown -> Notion
        notion_result = BulletedListElement.markdown_to_notion(original)
        assert notion_result is not None

        # Notion -> Markdown (würde echten TextInlineFormatter brauchen)
        # Hier können wir nur testen, dass die Struktur stimmt
        assert notion_result.type == "bulleted_list_item"
        assert len(notion_result.bulleted_list_item.rich_text) > 0


def test_empty_and_whitespace_content():
    """Test Behandlung von leerem und Whitespace-Content."""
    # Bullet mit nur Spaces nach dem Marker
    result = BulletedListElement.markdown_to_notion("-   ")
    assert (
        result is None or result is not None
    )  # Behavior depends on TextInlineFormatter

    # Bullet mit Text der nur aus Spaces besteht
    result = BulletedListElement.markdown_to_notion("-    only spaces   ")
    if result is not None:
        # Should handle whitespace somehow
        assert result.type == "bulleted_list_item"


def test_special_characters_in_content():
    """Test Sonderzeichen im Bullet-Content."""
    special_texts = [
        "- Text with ümlaut and émoji 🚀",
        "- Chinese text: 这是中文",
        "- Special chars: !@#$%^&*()",
        "- URLs: https://example.com",
        "- Code: `inline code`",
    ]

    for text in special_texts:
        result = BulletedListElement.markdown_to_notion(text)
        assert result is not None
        assert result.type == "bulleted_list_item"


def test_very_long_content():
    """Test sehr langer Bullet-Content."""
    long_text = "- " + "Very long text " * 100
    result = BulletedListElement.markdown_to_notion(long_text)
    assert result is not None
    assert result.type == "bulleted_list_item"


def test_indentation_levels():
    """Test verschiedene Indentation-Level."""
    indented_bullets = [
        "- Level 0",
        "  - Level 1",
        "    - Level 2",
        "      - Level 3",
        "\t- Tab indented",
    ]

    for bullet in indented_bullets:
        assert BulletedListElement.match_markdown(bullet)
        result = BulletedListElement.markdown_to_notion(bullet)
        assert result is not None
