from notionary.blocks.markdown.nodes import SpaceMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_space_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    """Test SpaceMarkdownNode"""
    space_syntax = syntax_registry.get_space_syntax()

    space = SpaceMarkdownNode()
    expected = space_syntax.start_delimiter
    assert space.to_markdown() == expected
