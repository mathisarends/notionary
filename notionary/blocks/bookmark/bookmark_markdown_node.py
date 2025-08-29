from __future__ import annotations

from typing import Optional

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class BookmarkMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced Bookmark node with Pydantic integration.
    Programmatic interface for creating Notion-style bookmark Markdown blocks.
    """

    url: str
    title: Optional[str] = None
    caption: Optional[str] = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [bookmark](https://example.com)
        - [bookmark](https://example.com)(caption:Some caption)
        """
        # Use simple bookmark syntax like BookmarkElement
        base_markdown = f"[bookmark]({self.url})"

        # Append caption using mixin helper
        return self.append_caption_to_markdown(base_markdown, self.caption)
