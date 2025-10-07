from notionary.blocks.markdown.nodes import TableOfContentsMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_table_of_contents_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    toc_syntax = syntax_registry.get_table_of_contents_syntax()

    toc = TableOfContentsMarkdownNode()
    expected = toc_syntax.start_delimiter
    assert toc.to_markdown() == expected

    toc2 = TableOfContentsMarkdownNode()
    expected = toc_syntax.start_delimiter
    assert toc2.to_markdown() == expected
