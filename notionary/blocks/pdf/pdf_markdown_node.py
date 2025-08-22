from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class PdfMarkdownNodeParams(BaseModel):
    url: str
    caption: Optional[str] = None


class PdfMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Programmatic interface for creating Notion-style Markdown PDF embeds.
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: PdfMarkdownNodeParams) -> PdfMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [pdf](https://example.com/document.pdf)
        - [pdf](https://example.com/document.pdf)(caption:Critical safety information)
        """
        base_markdown = f"[pdf]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
