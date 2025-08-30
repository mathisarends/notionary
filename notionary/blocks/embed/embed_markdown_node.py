from typing import Optional

from notionary.blocks.markdown.markdown_node import MarkdownNode


class EmbedMarkdownNode(MarkdownNode):
    """
    Enhanced Embed node with Pydantic integration.
    Programmatic interface for creating Notion-style Markdown embed blocks.
    Example: [embed](https://example.com "Optional caption")
    """

    url: str
    caption: Optional[str] = None

    def to_markdown(self) -> str:
        if self.caption:
            return f'[embed]({self.url} "{self.caption}")'
        return f"[embed]({self.url})"
