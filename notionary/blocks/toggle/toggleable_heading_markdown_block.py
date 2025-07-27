from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class ToggleableHeadingMarkdownBlockParams(BaseModel):
    text: str
    level: int = 1
    content: Optional[List[str]] = None


class ToggleableHeadingMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating collapsible Markdown headings (toggleable headings).
    Pipe-prefixed lines are used for the collapsible content.
    Example:
        +# Section
        | Hidden content
        +## Subsection
        | Details
    """

    def __init__(self, text: str, level: int = 1, content: Optional[list[str]] = None):
        if not (1 <= level <= 3):
            raise ValueError("Only heading levels 1-3 are supported (H1, H2, H3)")
        self.text = text
        self.level = level
        self.content = content or []

    @classmethod
    def from_params(
        cls, params: ToggleableHeadingMarkdownBlockParams
    ) -> ToggleableHeadingMarkdownBlock:
        return cls(text=params.text, level=params.level, content=params.content)

    def to_markdown(self) -> str:
        prefix = "+" + ("#" * self.level)
        result = f"{prefix} {self.text}"
        if self.content:
            result += "\n" + "\n".join([f"| {line}" for line in self.content])
        return result
