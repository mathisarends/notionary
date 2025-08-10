from __future__ import annotations
from typing import Optional

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class ColumnMarkdownBlockParams(BaseModel):
    children: list[MarkdownNode]
    width_ratio: Optional[float] = None
    model_config = {"arbitrary_types_allowed": True}


class ColumnMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating a single Markdown column block
    with pipe-prefixed nested content and optional width ratio.

    Example:
        ::: column
        | # Column Title
        |
        | Some content here
        :::

        ::: column 0.7
        | # Wide Column (70%)
        |
        | This column takes 70% width
        :::
    """

    def __init__(
        self, children: list[MarkdownNode], width_ratio: Optional[float] = None
    ):
        self.children = children
        self.width_ratio = width_ratio

    @classmethod
    def from_params(cls, params: ColumnMarkdownBlockParams) -> ColumnMarkdownNode:
        return cls(children=params.children, width_ratio=params.width_ratio)

    def to_markdown(self) -> str:
        # Start tag with optional width ratio
        if self.width_ratio is not None:
            start_tag = f"::: column {self.width_ratio}"
        else:
            start_tag = "::: column"

        if not self.children:
            return f"{start_tag}\n:::"

        # Convert children to markdown and add column prefix
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        # Add column prefix to each line (same logic as Toggle)
        lines = content_text.split("\n")
        prefixed_lines = [f"| {line}" if line.strip() else "|" for line in lines]

        return f"{start_tag}\n" + "\n".join(prefixed_lines) + "\n:::"
