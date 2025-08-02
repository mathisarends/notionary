"""
Pytest tests for ParagraphElement.
Tests conversion between Markdown paragraphs and Notion paragraph blocks.
"""

import pytest
from notionary.blocks.paragraph import ParagraphElement


@pytest.mark.parametrize(
    "text",
    [
        "Just some text",
        "",
        "    ",
        "*italic* and **bold**",
        "Paragraph with äöüß and 中文字符 and 🙂",
    ],
)
def test_match_markdown_always_true(text):
    """Paragraph is fallback element, always returns True."""
    assert ParagraphElement.match_markdown(text)


@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "paragraph"}, True),
        ({"type": "heading_1"}, False),
        ({"type": "quote"}, False),
        ({"notype": "paragraph"}, False),
        ({}, False),
    ],
)
def test_match_notion(block, expected):
    assert ParagraphElement.match_notion(block) is expected


def test_markdown_to_notion_basic():
    text = "This is a paragraph with *some* **formatting**."
    block = ParagraphElement.markdown_to_notion(text)
    assert block["type"] == "paragraph"
    assert "rich_text" in block["paragraph"]
    assert len(block["paragraph"]["rich_text"]) > 0
    # The content must be included somewhere
    all_content = "".join(
        [
            seg["text"]["content"]
            for seg in block["paragraph"]["rich_text"]
            if "text" in seg
        ]
    )
    assert "paragraph" in all_content


@pytest.mark.parametrize("text", ["", "   ", "\n", "\t"])
def test_markdown_to_notion_empty(text):
    # Returns None for empty or whitespace-only markdown
    assert ParagraphElement.markdown_to_notion(text) is None


def test_notion_to_markdown():
    block = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": "Some paragraph content"}}
            ]
        },
    }
    md = ParagraphElement.notion_to_markdown(block)
    assert md == "Some paragraph content"


def test_notion_to_markdown_unicode():
    block = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": "Mit Umlauten äöüß and 中文🙂👍"}}
            ]
        },
    }
    md = ParagraphElement.notion_to_markdown(block)
    assert "äöüß" in md
    assert "中文" in md
    assert "🙂" in md


def test_notion_to_markdown_empty():
    block = {"type": "paragraph", "paragraph": {"rich_text": []}}
    assert ParagraphElement.notion_to_markdown(block) is None


def test_notion_to_markdown_wrong_type():
    assert ParagraphElement.notion_to_markdown({"type": "heading_2"}) is None


def test_roundtrip():
    """Paragraph roundtrip: Markdown → Notion → Markdown"""
    text = "This is a test with *some* unicode äöüß 🙂👍"
    block = ParagraphElement.markdown_to_notion(text)
    assert block is not None
    # Compose markdown back
    md = ParagraphElement.notion_to_markdown(block)
    # Should contain original text, minus markdown formatting
    for part in ["test", "unicode", "äöüß", "🙂👍"]:
        assert part in md


@pytest.mark.parametrize(
    "content",
    [
        "Just plain text.",
        "Numbers 123456",
        "Mixed CAPS and lower",
        "Punctuation!?,.;:",
        "With\nnewlines\ninside",
    ],
)
def test_various_content(content):
    # Should convert and recover content, ignoring markdown formatting
    block = ParagraphElement.markdown_to_notion(content)
    md = ParagraphElement.notion_to_markdown(block)
    # Content may be merged or newlines removed, but base string should appear
    for word in content.replace("\n", " ").split():
        assert word.strip(".!?;,:") in md
