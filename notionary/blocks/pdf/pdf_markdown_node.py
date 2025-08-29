from __future__ import annotations

from typing import Optional

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin



class PdfMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Programmatic interface for creating Notion-style Markdown PDF embeds.
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [pdf](https://example.com/document.pdf)
        - [pdf](https://example.com/document.pdf)(caption:Critical safety information)
        """
        base_markdown = f"[pdf]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
