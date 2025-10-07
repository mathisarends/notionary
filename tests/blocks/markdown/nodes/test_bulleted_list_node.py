from notionary.blocks.markdown.nodes import BulletedListMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_bulleted_list_markdown_node() -> None:
    registry = SyntaxRegistry()
    bulleted_list_syntax = registry.get_bulleted_list_syntax()

    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"])
    expected = f"{bulleted_list_syntax.start_delimiter} Item 1\n{bulleted_list_syntax.start_delimiter} Item 2\n{bulleted_list_syntax.start_delimiter} Item 3"
    assert bulleted_list.to_markdown() == expected
