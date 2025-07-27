from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class ImageMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None
    alt: Optional[str] = None


class ImageMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown image blocks.
    Supports optional caption and alt text.
    Example: ![Caption](https://example.com/image.jpg "alt text")
    """

    def __init__(
        self, url: str, caption: Optional[str] = None, alt: Optional[str] = None
    ):
        self.url = url
        self.caption = caption or ""
        self.alt = alt

    @classmethod
    def from_params(cls, params: ImageMarkdownBlockParams) -> ImageMarkdownNode:
        return cls(url=params.url, caption=params.caption, alt=params.alt)

    def to_markdown(self) -> str:
        if self.alt:
            return f'![{self.caption}]({self.url} "{self.alt}")'
        return f"![{self.caption}]({self.url})"
