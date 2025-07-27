"""
Pytest tests for QuoteElement.
Tests conversion between Markdown quotes ([quote](text "author")) and Notion quote blocks.
"""

import pytest
from notionary.blocks import QuoteElement


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[quote](Simple quote text)", True),
        ('[quote](A quote "Author Name")', True),
        ("[quote](Another quote with emoji 🙂)", True),
        ("[quote](Multiline\nquote)", False),  # Multiline not supported in pattern
        ("[quote]()", False),  # Missing content
        ("[quot](Missing e)", False),
        ("No quote here", False),
        ("", False),
    ]
)
def test_match_markdown(text, expected):
    assert QuoteElement.match_markdown(text) is expected


@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "quote"}, True),
        ({"type": "paragraph"}, False),
        ({"type": "callout"}, False),
        ({}, False),
    ]
)
def test_match_notion(block, expected):
    assert QuoteElement.match_notion(block) is expected


@pytest.mark.parametrize(
    "markdown,exp_text,exp_author",
    [
        ("[quote](This is a quote)", "This is a quote", ""),
        ('[quote](With author "Steve Jobs")', "With author", "Steve Jobs"),
        ('[quote](Unicode test äöüß "Sören")', "Unicode test äöüß", "Sören"),
        ('[quote](Quote with emoji 🙂 "🧑‍💻")', "Quote with emoji 🙂", "🧑‍💻"),
    ]
)
def test_markdown_to_notion(markdown, exp_text, exp_author):
    block = QuoteElement.markdown_to_notion(markdown)
    assert block is not None
    assert block["type"] == "quote"
    text = block["quote"]["rich_text"][0]["text"]["content"]
    if exp_author:
        assert text == f"{exp_text}\n— {exp_author}"
    else:
        assert text == exp_text
    assert block["quote"]["color"] == "default"


@pytest.mark.parametrize(
    "markdown",
    [
        "[quote]()",
        "[quote](  )",
        "[quote](\n)",
        "[quote](Missing closing",
        "[quote](Text 'Wrong author quotes')",
        "[quote](Text \"author1\" \"author2\")",
        "Not a quote",
        "",
    ]
)
def test_markdown_to_notion_invalid(markdown):
    assert QuoteElement.markdown_to_notion(markdown) is None


@pytest.mark.parametrize(
    "notion_block,expected",
    [
        (
            {
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Only content"}}
                    ],
                    "color": "default",
                },
            },
            "[quote](Only content)",
        ),
        (
            {
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Some wise words\n— Alan"}}
                    ],
                    "color": "default",
                },
            },
            '[quote](Some wise words "Alan")',
        ),
        (
            {
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Mit Umlauten äöüß\n— Sören"}}
                    ],
                    "color": "default",
                },
            },
            '[quote](Mit Umlauten äöüß "Sören")',
        ),
    ]
)
def test_notion_to_markdown(notion_block, expected):
    md = QuoteElement.notion_to_markdown(notion_block)
    assert md == expected


@pytest.mark.parametrize(
    "block",
    [
        {"type": "paragraph"},
        {"type": "quote", "quote": {"rich_text": []}},
        {},
    ]
)
def test_notion_to_markdown_invalid(block):
    assert QuoteElement.notion_to_markdown(block) is None


def test_find_matches_basic():
    text = (
        "Intro text\n\n"
        "[quote](First quote)\n"
        "Some mid text\n"
        '[quote](Second "Author2")\n'
        "End."
    )
    matches = QuoteElement.find_matches(text)
    assert len(matches) == 2
    assert matches[0][2]["quote"]["rich_text"][0]["text"]["content"] == "First quote"
    assert matches[1][2]["quote"]["rich_text"][0]["text"]["content"] == "Second\n— Author2"


def test_find_matches_none():
    text = "No quotes here, just text."
    matches = QuoteElement.find_matches(text)
    assert matches == []


def test_find_matches_unicode():
    text = (
        '[quote](Mit Umlauten äöüß "Sören")\n'
        '[quote](With emoji 🙂 "🧑‍💻")'
    )
    matches = QuoteElement.find_matches(text)
    assert len(matches) == 2
    assert "äöüß" in matches[0][2]["quote"]["rich_text"][0]["text"]["content"]
    assert "🙂" in matches[1][2]["quote"]["rich_text"][0]["text"]["content"]


def test_is_multiline():
    assert not QuoteElement.is_multiline()


def test_roundtrip():
    markdowns = [
        "[quote](Simple text)",
        '[quote](Something wise "Socrates")',
        '[quote](Mit Umlauten äöüß "Sören")',
        '[quote](With emoji 🙂 "🧑‍💻")',
    ]
    for md in markdowns:
        block = QuoteElement.markdown_to_notion(md)
        assert block is not None
        recovered = QuoteElement.notion_to_markdown(block)
        assert recovered == md

