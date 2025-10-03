from notionary.blocks.markdown.nodes.base import MarkdownNode


class EmbedMarkdownNode(MarkdownNode):
    """
    Enhanced Embed node with Pydantic integration.
    Programmatic interface for creating Notion-style Markdown embed blocks.
    Example: [embed](https://example.com "Optional caption")
    """

    url: str
    caption: str | None = None

    def to_markdown(self) -> str:
        if self.caption:
            return f'[embed]({self.url} "{self.caption}")'
        return f"[embed]({self.url})"
