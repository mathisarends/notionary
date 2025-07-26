from typing import Optional

from notionary.blocks.mappings.markdown_node import MarkdownNode


class AudioMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Notion-style audio blocks.
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    def to_markdown(self) -> str:
        return f"$[{self.caption}]({self.url})"
