from notionary.blocks.markdown.nodes import BookmarkMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_bookmark_markdown_node() -> None:
    registry = SyntaxRegistry()
    bookmark_syntax = registry.get_bookmark_syntax()
    caption_syntax = registry.get_caption_syntax()

    bookmark = BookmarkMarkdownNode(url="https://example.com")
    expected = f"{bookmark_syntax.start_delimiter}https://example.com)"
    assert bookmark.to_markdown() == expected

    bookmark_with_caption = BookmarkMarkdownNode(url="https://example.com", caption="Example Site")
    expected = f"{bookmark_syntax.start_delimiter}https://example.com)\n{caption_syntax.start_delimiter} Example Site"
    assert bookmark_with_caption.to_markdown() == expected
