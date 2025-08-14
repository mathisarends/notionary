from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class PdfMarkdownNodeParams(BaseModel):
    url: str
    caption: Optional[str] = None


class PdfMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown PDF embeds.
    Example: [pdf](https://example.com/document.pdf "My Caption")
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: PdfMarkdownNodeParams) -> PdfMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        """
        Convert to markdown as [pdf](url "caption") or [pdf](url) if caption is empty.
        """
        if self.caption:
            return f'[pdf]({self.url} "{self.caption}")'
        return f"[pdf]({self.url})"
