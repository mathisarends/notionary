from notionary.blocks.markdown.nodes import BreadcrumbMarkdownNode


def test_breadcrumb_markdown_node() -> None:
    breadcrumb = BreadcrumbMarkdownNode()
    expected = "[breadcrumb]"
    assert breadcrumb.to_markdown() == expected
