import pytest

from notionary.page.content.markdown.nodes import SpaceMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def space_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_space_syntax().start_delimiter


def test_space_markdown_node(space_delimiter: str) -> None:
    space = SpaceMarkdownNode()
    expected = space_delimiter
    assert space.to_markdown() == expected
