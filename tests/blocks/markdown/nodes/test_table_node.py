from notionary.blocks.markdown.nodes import TableMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_table_markdown_node() -> None:
    """Test TableMarkdownNode"""
    registry = SyntaxRegistry()
    table_syntax = registry.get_table_syntax()

    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )
    expected = (
        f"{table_syntax.start_delimiter} Name {table_syntax.start_delimiter} Age {table_syntax.start_delimiter} City {table_syntax.start_delimiter}\n"
        f"{table_syntax.start_delimiter} {table_syntax.end_delimiter} {table_syntax.start_delimiter} {table_syntax.end_delimiter} {table_syntax.start_delimiter} {table_syntax.end_delimiter} {table_syntax.start_delimiter}\n"
        f"{table_syntax.start_delimiter} Alice {table_syntax.start_delimiter} 25 {table_syntax.start_delimiter} Berlin {table_syntax.start_delimiter}\n"
        f"{table_syntax.start_delimiter} Bob {table_syntax.start_delimiter} 30 {table_syntax.start_delimiter} Munich {table_syntax.start_delimiter}"
    )
    assert table.to_markdown() == expected
