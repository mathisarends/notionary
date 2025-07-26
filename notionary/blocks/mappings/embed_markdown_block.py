from typing import Optional
from notionary.blocks.mappings.markdown_node import MarkdownNode


class EmbedMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown embed blocks.
    Example: <embed:Caption>(https://example.com)
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    def to_markdown(self) -> str:
        if self.caption:
            return f"<embed:{self.caption}>({self.url})"
        return f"<embed>({self.url})"
