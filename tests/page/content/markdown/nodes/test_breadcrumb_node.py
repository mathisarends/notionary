import pytest

from notionary.page.content.markdown.nodes import BreadcrumbMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def breadcrumb_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_breadcrumb_syntax().start_delimiter


def test_breadcrumb_markdown_node(breadcrumb_delimiter: str) -> None:
    breadcrumb = BreadcrumbMarkdownNode()
    expected = breadcrumb_delimiter

    assert breadcrumb.to_markdown() == expected
