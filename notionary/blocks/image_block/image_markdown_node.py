from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class ImageMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None


class ImageMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Programmatic interface for creating Notion-style image blocks.
    """

    def __init__(
        self, url: str, caption: Optional[str] = None, alt: Optional[str] = None
    ):
        self.url = url
        self.caption = caption
        # Note: 'alt' is kept for API compatibility but not used in Notion syntax

    @classmethod
    def from_params(cls, params: ImageMarkdownBlockParams) -> ImageMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [image](https://example.com/screenshot.png)
        - [image](https://example.com/screenshot.png)(caption:Dashboard overview)
        """
        base_markdown = f"[image]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
