from __future__ import annotations

from typing import Optional

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class FileMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced File node with Pydantic integration.
    Programmatic interface for creating Notion-style Markdown file embeds.
    """
    url: str
    caption: Optional[str] = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [file](https://example.com/document.pdf)
        - [file](https://example.com/document.pdf)(caption:User manual)
        """
        base_markdown = f"[file]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
