from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode


class FileMarkdownNodeParams(BaseModel):
    url: str
    caption: Optional[str] = None


class FileMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown file embeds.
    Example: [file](https://example.com/file.pdf "My Caption")
    """

    def __init__(self, url: str, caption: Optional[str] = None):
        self.url = url
        self.caption = caption or ""

    @classmethod
    def from_params(cls, params: FileMarkdownNodeParams) -> FileMarkdownNode:
        return cls(url=params.url, caption=params.caption)

    def to_markdown(self) -> str:
        """
        Convert to markdown as [file](url "caption") or [file](url) if caption is empty.
        """
        if self.caption:
            return f'[file]({self.url} "{self.caption}")'
        return f"[file]({self.url})"
