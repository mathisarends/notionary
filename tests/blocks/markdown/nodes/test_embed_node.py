from notionary.blocks.markdown.nodes import EmbedMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_embed_markdown_node() -> None:
    registry = SyntaxRegistry()
    embed_syntax = registry.get_embed_syntax()
    caption_syntax = registry.get_caption_syntax()

    embed = EmbedMarkdownNode(url="https://example.com")
    expected = f"{embed_syntax.start_delimiter}https://example.com)"
    assert embed.to_markdown() == expected

    embed_with_caption = EmbedMarkdownNode(url="https://example.com", caption="External content")
    expected = f"{embed_syntax.start_delimiter}https://example.com)\n{caption_syntax.start_delimiter} External content"
    assert embed_with_caption.to_markdown() == expected
