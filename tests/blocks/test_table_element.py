"""
Pytest tests for TableElement.
Tests conversion between Markdown tables and Notion table blocks.
"""

import pytest
from notionary.blocks import TableElement

@pytest.fixture
def markdown_table():
    return (
        "| Name    | Age | City      |\n"
        "|---------|-----|-----------|\n"
        "| Alice   | 30  | New York  |\n"
        "| Bob     | 25  | Berlin    |"
    )

@pytest.fixture
def notion_table():
    notion_tbl = {
        "type": "table",
        "table": {
            "table_width": 3,
            "has_column_header": True,
            "has_row_header": False,
            "children": [
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Name"}}],
                            [{"type": "text", "text": {"content": "Age"}}],
                            [{"type": "text", "text": {"content": "City"}}],
                        ]
                    },
                },
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Alice"}}],
                            [{"type": "text", "text": {"content": "30"}}],
                            [{"type": "text", "text": {"content": "New York"}}],
                        ]
                    },
                },
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Bob"}}],
                            [{"type": "text", "text": {"content": "25"}}],
                            [{"type": "text", "text": {"content": "Berlin"}}],
                        ]
                    },
                },
            ],
        },
        "children": [],  # gets filled for export
    }
    # Simulate Notion structure with children at top level
    notion_tbl["children"] = notion_tbl["table"]["children"]
    return notion_tbl


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "| Col1 | Col2 |\n|------|------|\n| a    | b    |",
            True,
        ),
        (
            "Just some text\nAnother line",
            False,
        ),
        (
            "| Header |\n|--------|\n",
            True,
        ),
        (
            "",
            False,
        ),
    ],
)
def test_match_markdown(text, expected):
    assert TableElement.match_markdown(text) == expected


def test_match_notion(notion_table):
    assert TableElement.match_notion(notion_table)
    assert not TableElement.match_notion({"type": "paragraph"})


def test_markdown_to_notion(markdown_table):
    block = TableElement.markdown_to_notion(markdown_table)
    assert block is not None
    assert block["type"] == "table"
    assert block["table"]["table_width"] == 3
    assert len(block["table"]["children"]) == 3


def test_markdown_to_notion_invalid():
    invalid_md = "Not a table\nStill not a table"
    assert TableElement.markdown_to_notion(invalid_md) is None


def test_notion_to_markdown(notion_table):
    markdown = TableElement.notion_to_markdown(notion_table)
    assert "| Name" in markdown
    assert "| Alice" in markdown
    assert "| Bob" in markdown
    # Standard Markdown table divider (optional, could be just dashes too)
    assert "| -------- |" in markdown or "|-----|" in markdown


def test_notion_to_markdown_empty():
    empty_table = {
        "type": "table",
        "table": {
            "table_width": 2,
            "has_column_header": True,
            "has_row_header": False,
        },
        "children": [],
    }
    md = TableElement.notion_to_markdown(empty_table)
    assert "| Column 1 | Column 2 |" in md
    assert "| -------- | -------- |" in md


def test_find_matches():
    text = (
        "Intro\n\n"
        "| H1 | H2 |\n"
        "|----|----|\n"
        "| A1 | A2 |\n\n"
        "End"
    )
    matches = TableElement.find_matches(text)
    assert len(matches) == 1
    start, end, block = matches[0]
    assert start < end
    assert block["type"] == "table"


def test_is_multiline():
    assert TableElement.is_multiline()


@pytest.mark.parametrize(
    "md",
    [
        "| Title | Value |\n|-------|-------|\n| Foo   | Bar   |",
        "| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |",
    ]
)
def test_roundtrip_markdown_notion_markdown(md):
    block = TableElement.markdown_to_notion(md)
    assert block is not None
    result_md = TableElement.notion_to_markdown(block)
    # At least check all original headers are in the output
    for header in md.splitlines()[0].split("|")[1:-1]:
        assert header.strip() in result_md

