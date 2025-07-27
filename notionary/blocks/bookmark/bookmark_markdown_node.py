from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from notionary.blocks.markdown_node import MarkdownNode


class BookmarkMarkdownBlockParams(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None


class BookmarkMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style bookmark Markdown blocks.
    """

    def __init__(
        self, url: str, title: Optional[str] = None, description: Optional[str] = None
    ):
        self.url = url
        self.title = title
        self.description = description

    @classmethod
    def from_params(cls, params: BookmarkMarkdownBlockParams) -> BookmarkMarkdownNode:
        return cls(url=params.url, title=params.title, description=params.description)

    def to_markdown(self) -> str:
        """
        Returns the Markdown representation, e.g.:
        [bookmark](https://example.com "Title" "Description")
        """
        parts = [f"[bookmark]({self.url}"]
        if self.title is not None:
            parts.append(f'"{self.title}"')
        if self.description is not None:
            # Wenn title fehlt, aber description da ist, trotzdem Platzhalter für title:
            if self.title is None:
                parts.append('""')
            parts.append(f'"{self.description}"')
        return " ".join(parts) + ")"
