from notionary.page.content.markdown.nodes import BreadcrumbMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_breadcrumb_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    breadcrumb_syntax = syntax_registry.get_breadcrumb_syntax()

    breadcrumb = BreadcrumbMarkdownNode()
    expected = breadcrumb_syntax.start_delimiter
    assert breadcrumb.to_markdown() == expected
