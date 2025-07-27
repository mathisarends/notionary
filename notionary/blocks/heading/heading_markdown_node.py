from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class HeadingMarkdownBlockParams(BaseModel):
    text: str
    level: int = 1


class HeadingMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown headings (H1-H3).
    Example: # Heading 1, ## Heading 2, ### Heading 3
    """

    def __init__(self, text: str, level: int = 1):
        if not (1 <= level <= 3):
            raise ValueError("Only heading levels 1-3 are supported (H1, H2, H3)")
        self.text = text
        self.level = level

    @classmethod
    def from_params(cls, params: HeadingMarkdownBlockParams) -> HeadingMarkdownNode:
        return cls(text=params.text, level=params.level)

    def to_markdown(self) -> str:
        return f"{'#' * self.level} {self.text}"
