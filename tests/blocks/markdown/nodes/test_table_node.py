from notionary.blocks.markdown.nodes import TableMarkdownNode


def test_table_markdown_node() -> None:
    """Test TableMarkdownNode"""
    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )
    expected = (
        "| Name | Age | City |\n| -------- | -------- | -------- |\n| Alice | 25 | Berlin |\n| Bob | 30 | Munich |"
    )
    assert table.to_markdown() == expected
