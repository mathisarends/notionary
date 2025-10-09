from notionary.page.content.markdown.nodes import NumberedListMarkdownNode


def test_numbered_list_markdown_node(syntax_registry) -> None:
    numbered_list_syntax = syntax_registry.get_numbered_list_syntax()

    numbered_list = NumberedListMarkdownNode(texts=["First", "Second", "Third"])
    expected = f"1{numbered_list_syntax.end_delimiter} First\n2{numbered_list_syntax.end_delimiter} Second\n3{numbered_list_syntax.end_delimiter} Third"
    assert numbered_list.to_markdown() == expected
