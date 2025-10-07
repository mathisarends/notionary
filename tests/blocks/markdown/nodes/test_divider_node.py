from notionary.blocks.markdown.nodes import DividerMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_divider_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    divider_syntax = syntax_registry.get_divider_syntax()

    divider = DividerMarkdownNode()
    expected = divider_syntax.start_delimiter
    assert divider.to_markdown() == expected
