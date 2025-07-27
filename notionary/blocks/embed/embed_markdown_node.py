from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.toggle.markdown_node import MarkdownNode


class EmbedMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None


class EmbedMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown embed blocks.
    Example: <embed:Caption>(https://example.com)
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: EmbedMarkdownBlockParams) -> EmbedMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        if self.caption:
            return f"<embed:{self.caption}>({self.url})"
        return f"<embed>({self.url})"
