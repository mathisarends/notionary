from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class AudioMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Programmatic interface for creating Notion-style audio blocks.
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [audio](https://example.com/song.mp3)
        - [audio](https://example.com/song.mp3)(caption:Background music)
        """
        base_markdown = f"[audio]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
