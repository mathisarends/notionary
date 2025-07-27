"""
Pytest tests for NumberedListElement.
Tests conversion between Markdown numbered lists and Notion numbered_list_item blocks.
"""

import pytest
from notionary.blocks import NumberedListElement


@pytest.mark.parametrize(
    "markdown,expected",
    [
        ("1. First item", True),
        ("42. Item number 42", True),
        ("1234567890. Big number", True),
        ("- Not numbered", False),
        ("No list here", False),
        (" 1. Leading space", True),
        ("001. Padded number", True),
        ("1 . With space after number", False),
        ("1.First item (no space)", False),
        ("", False),
    ],
)
def test_match_markdown(markdown, expected):
    assert NumberedListElement.match_markdown(markdown) is expected


@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "numbered_list_item"}, True),
        ({"type": "heading_1"}, False),
        ({"type": "bulleted_list_item"}, False),
        ({}, False),
        ({"block_type": "numbered_list_item"}, False),
    ],
)
def test_match_notion(block, expected):
    assert NumberedListElement.match_notion(block) is expected


def test_markdown_to_notion():
    result = NumberedListElement.markdown_to_notion("1. Numbered item")
    assert result is not None
    assert result["type"] == "numbered_list_item"
    rich_text = result["numbered_list_item"]["rich_text"]
    assert rich_text[0]["text"]["content"] == "Numbered item"

    # Edge: Leading space and high number
    r2 = NumberedListElement.markdown_to_notion(" 42. The Answer")
    assert r2["numbered_list_item"]["rich_text"][0]["text"]["content"] == "The Answer"


def test_markdown_to_notion_invalid():
    # Invalid: no number or wrong syntax
    assert NumberedListElement.markdown_to_notion("- Not a numbered list") is None
    assert NumberedListElement.markdown_to_notion("Not a list at all") is None
    assert NumberedListElement.markdown_to_notion("") is None
    assert NumberedListElement.markdown_to_notion("1 . Space after dot") is None
    assert NumberedListElement.markdown_to_notion("1.First (no space)") is None


def test_notion_to_markdown():
    block = {
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Second item"}}],
            "color": "default",
        },
    }
    md = NumberedListElement.notion_to_markdown(block)
    assert md == "1. Second item"  # always starts at 1.


def test_notion_to_markdown_invalid():
    # Invalid: wrong type
    assert NumberedListElement.notion_to_markdown({"type": "heading_1"}) is None
    # Missing numbered_list_item
    assert (
        NumberedListElement.notion_to_markdown({"type": "numbered_list_item"}) is None
    )
    # Wrong structure
    assert (
        NumberedListElement.notion_to_markdown(
            {"type": "numbered_list_item", "numbered_list_item": {}}
        )
        == "1. "
    )


def test_is_multiline():
    assert not NumberedListElement.is_multiline()


def test_roundtrip():
    """Markdown -> Notion -> Markdown keeps content (with '1.' prefix)"""
    markdowns = [
        "1. Alpha",
        "23. Bravo",
        "001. Charlie",
        "123456. Long number",
    ]
    for md in markdowns:
        notion = NumberedListElement.markdown_to_notion(md)
        assert notion is not None
        back = NumberedListElement.notion_to_markdown(notion)
        # Always normalizes to "1. content"
        assert back.startswith("1. ")
        assert back[3:] == md[md.find(".") + 1 :].strip()


@pytest.mark.parametrize(
    "text",
    [
        "1. Mit Umlauten äöüß",
        "42. 中文内容",
        "1. Emoji 🙂👍",
        "77. Special !?&/()[]",
    ],
)
def test_unicode_content(text):
    block = NumberedListElement.markdown_to_notion(text)
    assert block is not None
    rich = block["numbered_list_item"]["rich_text"]
    assert rich[0]["text"]["content"] in text

    back = NumberedListElement.notion_to_markdown(block)
    # Always normalizes to "1. ..."
    assert back.startswith("1. ")
    assert rich[0]["text"]["content"] in back
