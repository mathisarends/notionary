from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class DocumentMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None


class DocumentMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown document/file embeds.
    Example: %[My Caption](https://example.com/file.pdf)
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: DocumentMarkdownBlockParams) -> DocumentMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        return f"%[{self.caption}]({self.url})"
