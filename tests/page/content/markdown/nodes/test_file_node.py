import pytest

from notionary.page.content.markdown.nodes import FileMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


@pytest.fixture
def file_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_file_syntax().start_delimiter


def test_file_without_caption(file_delimiter: str) -> None:
    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = f"{file_delimiter}https://example.com/doc.pdf)"

    assert file.to_markdown() == expected


def test_file_with_caption(file_delimiter: str, caption_delimiter: str) -> None:
    file = FileMarkdownNode(url="https://example.com/doc.pdf", caption="Important Document")
    expected = f"{file_delimiter}https://example.com/doc.pdf)\n{caption_delimiter} Important Document"

    assert file.to_markdown() == expected
