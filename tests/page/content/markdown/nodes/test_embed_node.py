import pytest

from notionary.page.content.markdown.nodes import EmbedMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def embed_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_embed_syntax().start_delimiter


def test_embed_without_caption(embed_delimiter: str) -> None:
    embed = EmbedMarkdownNode(url="https://example.com")
    expected = f"{embed_delimiter}https://example.com)"

    assert embed.to_markdown() == expected


def test_embed_with_caption(embed_delimiter: str, caption_delimiter: str) -> None:
    embed = EmbedMarkdownNode(url="https://example.com", caption="External content")
    expected = f"{embed_delimiter}https://example.com)\n{caption_delimiter} External content"

    assert embed.to_markdown() == expected
