"""
Pytest tests for ToggleElement.
Tests conversion between Markdown toggles and Notion toggle blocks.
"""

import pytest
from notionary.blocks import ToggleElement

@pytest.mark.parametrize(
    "text,expected",
    [
        ("+++ This is a toggle", True),
        ("+++   Another one", True),
        ("++ Not a toggle", False),
        ("> Blockquote", False),
        ("+++", False),
        ("", False),
        ("+++    ", False),
        ("Some text", False),
    ]
)
def test_match_markdown(text, expected):
    assert ToggleElement.match_markdown(text) == expected

@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "toggle"}, True),
        ({"type": "paragraph"}, False),
        ({"type": "callout"}, False),
        ({}, False),
    ]
)
def test_match_notion(block, expected):
    assert ToggleElement.match_notion(block) == expected

def test_markdown_to_notion_valid():
    markdown = "+++ My Toggle Title"
    expected = {
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "My Toggle Title"}}],
            "color": "default",
            "children": [],
        },
    }
    assert ToggleElement.markdown_to_notion(markdown) == expected

@pytest.mark.parametrize("invalid", [
    "+++",             # No title
    "This is just text",
    "++ No toggle",
    "",
])
def test_markdown_to_notion_invalid(invalid):
    assert ToggleElement.markdown_to_notion(invalid) is None

def test_notion_to_markdown_simple():
    notion_block = {
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "My Toggle Title"}}],
            "color": "default",
            "children": [],
        },
    }
    assert ToggleElement.notion_to_markdown(notion_block) == "+++ My Toggle Title"

def test_notion_to_markdown_with_children():
    # Nested children render as placeholder
    notion_with_children = {
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "Parent"}}],
            "color": "default",
            "children": [{"type": "paragraph", "paragraph": {"rich_text": []}}],
        },
    }
    result = ToggleElement.notion_to_markdown(notion_with_children)
    assert result.startswith("+++ Parent")
    assert "[Nested content]" in result

def test_notion_to_markdown_invalid():
    assert ToggleElement.notion_to_markdown({"type": "paragraph"}) is None
    assert ToggleElement.notion_to_markdown({}) is None

def test_is_multiline():
    assert ToggleElement.is_multiline()

@pytest.mark.parametrize(
    "md",
    [
        "+++ Toggle mit Umlauten äöüß",
        "+++ Toggle mit Emoji 🙂",
        "+++    Spaces vorne und hinten   ",
    ]
)
def test_unicode_content_and_whitespace(md):
    block = ToggleElement.markdown_to_notion(md)
    assert block is not None
    # The content must appear in the Notion block's text
    text = block["toggle"]["rich_text"][0]["text"]["content"]
    for word in md.lstrip("+").strip().split():
        if word not in ("Toggle", "mit", "Umlauten", "Emoji", "Spaces", "vorne", "und", "hinten"):
            assert word in text or text.endswith(word)

def test_roundtrip():
    cases = [
        "+++ Einfache Überschrift",
        "+++ Toggle mit Emoji 🚀",
        "+++   Mit mehreren   Spaces   ",
    ]
    for md in cases:
        block = ToggleElement.markdown_to_notion(md)
        md2 = ToggleElement.notion_to_markdown(block)
        # Remove redundant spaces for matching
        assert md2.startswith("+++")
        for word in md.lstrip("+").strip().split():
            assert word in md2

