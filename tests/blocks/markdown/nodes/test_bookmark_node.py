from notionary.blocks.markdown.nodes import BookmarkMarkdownNode


def test_bookmark_markdown_node() -> None:
    bookmark = BookmarkMarkdownNode(url="https://example.com")
    expected = "[bookmark](https://example.com)"
    assert bookmark.to_markdown() == expected

    bookmark_with_caption = BookmarkMarkdownNode(url="https://example.com", caption="Example Site")
    expected = "[bookmark](https://example.com)(caption:Example Site)"
    assert bookmark_with_caption.to_markdown() == expected
