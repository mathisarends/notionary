import pytest

from notionary.page.content.markdown.nodes import BookmarkMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def bookmark_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_bookmark_syntax().start_delimiter


def test_bookmark_without_caption(bookmark_delimiter: str) -> None:
    bookmark = BookmarkMarkdownNode(url="https://example.com")
    expected = f"{bookmark_delimiter}https://example.com)"

    assert bookmark.to_markdown() == expected


def test_bookmark_with_caption(bookmark_delimiter: str, caption_delimiter: str) -> None:
    bookmark = BookmarkMarkdownNode(url="https://example.com", caption="Example Site")
    expected = (
        f"{bookmark_delimiter}https://example.com)\n{caption_delimiter} Example Site"
    )

    assert bookmark.to_markdown() == expected
