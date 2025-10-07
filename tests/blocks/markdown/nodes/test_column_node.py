from notionary.blocks.markdown.nodes import (
    ColumnMarkdownNode,
    HeadingMarkdownNode,
    ParagraphMarkdownNode,
)
from notionary.page.content.syntax.service import SyntaxRegistry


def test_column_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    column_syntax = syntax_registry.get_column_syntax()
    heading_syntax = syntax_registry.get_heading_syntax()

    column_empty = ColumnMarkdownNode(children=[])
    expected = f"{column_syntax.start_delimiter}\n{column_syntax.end_delimiter}"
    assert column_empty.to_markdown() == expected

    children = [
        HeadingMarkdownNode(text="Column Title", level=2),
        ParagraphMarkdownNode(text="Column content here"),
    ]
    column_with_content = ColumnMarkdownNode(children=children)
    expected = f"{column_syntax.start_delimiter}\n{heading_syntax.start_delimiter * 2} Column Title\n\nColumn content here\n{column_syntax.end_delimiter}"
    assert column_with_content.to_markdown() == expected


def test_column_markdown_node_with_width_ratio(syntax_registry: SyntaxRegistry) -> None:
    column_syntax = syntax_registry.get_column_syntax()

    column_with_ratio = ColumnMarkdownNode(children=[], width_ratio=0.5)
    expected = f"{column_syntax.start_delimiter} 0.5\n{column_syntax.end_delimiter}"
    assert column_with_ratio.to_markdown() == expected

    children = [ParagraphMarkdownNode(text="Half width column")]
    column_with_ratio_and_content = ColumnMarkdownNode(children=children, width_ratio=0.3)
    expected = f"{column_syntax.start_delimiter} 0.3\nHalf width column\n{column_syntax.end_delimiter}"
    assert column_with_ratio_and_content.to_markdown() == expected
