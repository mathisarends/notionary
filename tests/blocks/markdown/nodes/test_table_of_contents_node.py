from notionary.blocks.markdown.nodes import TableOfContentsMarkdownNode


def test_table_of_contents_markdown_node() -> None:
    toc = TableOfContentsMarkdownNode()
    expected = "[toc]"
    assert toc.to_markdown() == expected

    toc2 = TableOfContentsMarkdownNode()
    expected = "[toc]"
    assert toc2.to_markdown() == expected
