from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class ColumnMarkdownBlockParams(BaseModel):
    children: list[MarkdownNode]
    model_config = {"arbitrary_types_allowed": True}


class ColumnMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating a single Markdown column block
    with pipe-prefixed nested content using MarkdownNode children.

    Example:
        ::: column
        | # Column Title
        |
        | Some content here
        |
        | - List item 1
        | - List item 2
        |
        | ```python
        | print("code example")
        | ```
        :::
    """

    def __init__(self, children: list[MarkdownNode]):
        self.children = children

    @classmethod
    def from_params(cls, params: ColumnMarkdownBlockParams) -> ColumnMarkdownNode:
        return cls(children=params.children)

    def to_markdown(self) -> str:
        if not self.children:
            return "::: column\n:::"

        # Convert children to markdown and add column prefix
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        # Add column prefix to each line (same logic as Toggle)
        lines = content_text.split("\n")
        prefixed_lines = [f"| {line}" if line.strip() else "|" for line in lines]

        return "::: column\n" + "\n".join(prefixed_lines) + "\n:::"