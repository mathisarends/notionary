from notionary.blocks.markdown.nodes import (
    ColumnMarkdownNode,
    HeadingMarkdownNode,
    ParagraphMarkdownNode,
)


def test_column_markdown_node() -> None:
    column_empty = ColumnMarkdownNode(children=[])
    expected = "::: column\n:::"
    assert column_empty.to_markdown() == expected

    children = [
        HeadingMarkdownNode(text="Column Title", level=2),
        ParagraphMarkdownNode(text="Column content here"),
    ]
    column_with_content = ColumnMarkdownNode(children=children)
    expected = "::: column\n## Column Title\n\nColumn content here\n:::"
    assert column_with_content.to_markdown() == expected
