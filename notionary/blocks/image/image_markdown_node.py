from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class ImageMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None


class ImageMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style image blocks.
    Example: [image](https://example.com/image.jpg "Optional caption")
    """

    def __init__(self, url: str, caption: Optional[str] = None, alt: Optional[str] = None):
        self.url = url
        self.caption = caption
        # Note: 'alt' is kept for API compatibility but not used in Notion syntax

    @classmethod
    def from_params(cls, params: ImageMarkdownBlockParams) -> ImageMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        if self.caption:
            return f'[image]({self.url} "{self.caption}")'
        return f"[image]({self.url})"