"""
Pytest tests for TodoElement.
Tests conversion between Markdown todos and Notion to_do blocks.
"""

import pytest
from notionary.blocks.todo import TodoElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


@pytest.mark.parametrize(
    "line,expected",
    [
        ("- [ ] Unchecked todo", True),
        ("* [ ] Unchecked todo", True),
        ("+ [ ] Unchecked todo", True),
        ("  - [ ] Indented todo", True),
        ("- [x] Checked todo", True),
        ("* [x] Checked todo", True),
        ("+ [x] Checked todo", True),
        ("- Regular list item", False),
        ("[ ] Not a todo", False),
        ("- [o] Invalid checkbox", False),
        ("", False),
    ],
)
def test_match_markdown(line, expected):
    assert TodoElement.match_markdown(line) == expected


@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "to_do"}, True),
        ({"type": "paragraph"}, False),
        ({"type": "bulleted_list_item"}, False),
        ({"type": "something_else"}, False),
        ({}, False),
    ],
)
def test_match_notion(block, expected):
    assert TodoElement.match_notion(block) == expected


@pytest.mark.parametrize(
    "md,checked,expected_text",
    [
        ("- [ ] Buy groceries", False, "Buy groceries"),
        ("- [x] Complete assignment", True, "Complete assignment"),
        ("* [ ] Call Mom", False, "Call Mom"),
        ("+ [x] Pay bills", True, "Pay bills"),
        ("  - [ ] Indented", False, "Indented"),
    ],
)
def test_markdown_to_notion(md, checked, expected_text):
    block = TodoElement.markdown_to_notion(md)
    assert block["type"] == "to_do"
    assert block["to_do"]["checked"] == checked
    assert block["to_do"]["color"] == "default"
    extracted = TextInlineFormatter.extract_text_with_formatting(
        block["to_do"]["rich_text"]
    )
    assert expected_text in extracted


@pytest.mark.parametrize(
    "md",
    ["- Regular list item", "[ ] Not a todo", "- [o] Invalid checkbox", "", "nope"],
)
def test_markdown_to_notion_invalid(md):
    assert TodoElement.markdown_to_notion(md) is None


def test_notion_to_markdown_unchecked():
    block = TodoElement._create_todo_block("Buy groceries", False)
    markdown = TodoElement.notion_to_markdown(block)
    assert markdown == "- [ ] Buy groceries"


def test_notion_to_markdown_checked():
    block = TodoElement._create_todo_block("Complete assignment", True)
    markdown = TodoElement.notion_to_markdown(block)
    assert markdown == "- [x] Complete assignment"


def test_notion_to_markdown_invalid():
    assert TodoElement.notion_to_markdown({"type": "paragraph"}) is None


def test_with_formatting():
    todo_with_formatting = "- [ ] Remember to *buy* **groceries**"
    notion_block = TodoElement.markdown_to_notion(todo_with_formatting)
    markdown = TodoElement.notion_to_markdown(notion_block)
    # Should contain the plain text segments and keep the todo structure
    assert "Remember to" in markdown
    assert "buy" in markdown
    assert "groceries" in markdown
    assert markdown.startswith("- [ ] ")


def test_is_multiline():
    assert not TodoElement.is_multiline()


@pytest.mark.parametrize(
    "md",
    [
        "- [ ] Käse kaufen",
        "- [x] Aufgabe erledigt 🙂",
        "* [x] Mit Unicode äöüß",
        "+ [ ] Todo mit Emoji 👍",
    ],
)
def test_unicode_content(md):
    block = TodoElement.markdown_to_notion(md)
    text = TextInlineFormatter.extract_text_with_formatting(block["to_do"]["rich_text"])
    for word in md.split():
        if word not in "- [ ] [x] * +":
            assert any(c in text for c in word if c.isalnum() or c in "äöüß🙂👍")


def test_roundtrip():
    cases = [
        "- [ ] Do homework",
        "- [x] Submit report",
        "* [ ] Walk the dog",
        "+ [x] Finish project",
        "- [ ] 🥦 Gemüse kaufen",
        "- [x] Aufgabe erledigt 🙂",
    ]
    for md in cases:
        block = TodoElement.markdown_to_notion(md)
        back = TodoElement.notion_to_markdown(block)
        # The checkbox and text must be preserved
        assert back.startswith("- [ ]") or back.startswith("- [x]")
        # The main text should appear somewhere in the output
        for word in md[6:].strip().split():
            assert word.strip() in back
