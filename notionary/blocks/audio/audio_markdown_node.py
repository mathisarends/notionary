from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from notionary.blocks.markdown_node import MarkdownNode


class AudioMarkdownBlockParams(BaseModel):
    url: str
    caption: Optional[str] = None


class AudioMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style audio blocks.
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: AudioMarkdownBlockParams) -> AudioMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        return f"$[{self.caption}]({self.url})"
