import pytest

from notionary.blocks.markdown.nodes import HeadingMarkdownNode


def test_heading_markdown_node() -> None:
    h1 = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = "# Heading 1"
    assert h1.to_markdown() == expected

    h2 = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = "## Heading 2"
    assert h2.to_markdown() == expected

    h3 = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = "### Heading 3"
    assert h3.to_markdown() == expected

    with pytest.raises(ValueError):
        HeadingMarkdownNode(text="Invalid", level=4)
