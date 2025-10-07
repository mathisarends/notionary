from notionary.blocks.markdown.nodes import NumberedListMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_numbered_list_markdown_node() -> None:
    registry = SyntaxRegistry()
    numbered_list_syntax = registry.get_numbered_list_syntax()

    numbered_list = NumberedListMarkdownNode(texts=["First", "Second", "Third"])
    expected = f"1{numbered_list_syntax.end_delimiter} First\n2{numbered_list_syntax.end_delimiter} Second\n3{numbered_list_syntax.end_delimiter} Third"
    assert numbered_list.to_markdown() == expected
