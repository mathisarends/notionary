import pytest

from notionary.markdown.nodes import TableOfContentsMarkdownNode
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


@pytest.fixture
def table_of_contents_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_table_of_contents_syntax().start_delimiter


def test_table_of_contents_markdown_node(table_of_contents_delimiter: str) -> None:
    toc = TableOfContentsMarkdownNode()
    expected = table_of_contents_delimiter

    assert toc.to_markdown() == expected
