from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class ToggleMarkdownBlockParams(BaseModel):
    title: str
    content: Optional[List[str]] = None


class ToggleMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown toggle blocks
    with pipe-prefixed nested content.
    Example:
        +++ Details
        | Here are the details.
        | You can add more lines.
    """

    def __init__(self, title: str, content: Optional[List[str]] = None):
        self.title = title
        self.content = content or []

    @classmethod
    def from_params(cls, params: ToggleMarkdownBlockParams) -> ToggleMarkdownNode:
        return cls(title=params.title, content=params.content)

    def to_markdown(self) -> str:
        result = f"+++ {self.title}"
        if self.content:
            result += "\n" + "\n".join([f"| {line}" for line in self.content])
        return result
