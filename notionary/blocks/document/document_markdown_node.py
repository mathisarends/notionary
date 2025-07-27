from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode

class DocumentMarkdownNodeParams(BaseModel):
    url: str
    caption: Optional[str] = None

class DocumentMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown document/file embeds.
    Example: [document](https://example.com/file.pdf "My Caption")
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: DocumentMarkdownNodeParams) -> DocumentMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        """
        Convert to markdown as [document](url "caption") or [document](url) if caption is empty.
        """
        if self.caption:
            return f'[document]({self.url} "{self.caption}")'
        return f'[document]({self.url})'
