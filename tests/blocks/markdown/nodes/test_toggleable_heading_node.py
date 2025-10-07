import pytest

from notionary.blocks.markdown.nodes import (
    ParagraphMarkdownNode,
    ToggleableHeadingMarkdownNode,
)


def test_toggleable_heading_markdown_node() -> None:
    toggleable_h1 = ToggleableHeadingMarkdownNode(text="Section 1", level=1, children=[])
    expected = "+++# Section 1\n+++"
    assert toggleable_h1.to_markdown() == expected

    # Test mit Content - korrekte Syntax mit +++
    toggleable_h2 = ToggleableHeadingMarkdownNode(
        text="Section 2",
        level=2,
        children=[
            ParagraphMarkdownNode(text="Content line 1"),
            ParagraphMarkdownNode(text="Content line 2"),
        ],
    )
    expected = "+++## Section 2\nContent line 1\n\nContent line 2\n+++"
    assert toggleable_h2.to_markdown() == expected

    # Test ungültiges Level
    with pytest.raises(ValueError):
        ToggleableHeadingMarkdownNode(text="Invalid", level=4, children=[])
