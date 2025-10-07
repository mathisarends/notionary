from notionary.blocks.markdown.nodes import EmbedMarkdownNode


def test_embed_markdown_node() -> None:
    embed = EmbedMarkdownNode(url="https://example.com")
    expected = "[embed](https://example.com)"
    assert embed.to_markdown() == expected

    embed_with_caption = EmbedMarkdownNode(url="https://example.com", caption="External content")
    expected = '[embed](https://example.com "External content")'
    assert embed_with_caption.to_markdown() == expected
