from notionary.page.content.markdown.nodes import EmbedMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


def test_embed_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    embed_syntax = syntax_registry.get_embed_syntax()

    embed = EmbedMarkdownNode(url="https://example.com")
    expected = f"{embed_syntax.start_delimiter}https://example.com)"
    assert embed.to_markdown() == expected

    embed_with_caption = EmbedMarkdownNode(url="https://example.com", caption="External content")
    expected = f"{embed_syntax.start_delimiter}https://example.com)\n{caption_syntax.start_delimiter} External content"
    assert embed_with_caption.to_markdown() == expected
