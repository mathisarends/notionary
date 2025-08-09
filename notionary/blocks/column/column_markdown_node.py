from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class ColumnMarkdownBlockParams(BaseModel):
    children: list[MarkdownNode]
    model_config = {"arbitrary_types_allowed": True}


class ColumnMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating a single Markdown column block.
    This represents one column within a column layout.

    Example:
    ::: column
    # Column Title
    Some content here
    - List item 1
    - List item 2
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

        content_parts = [child.to_markdown() for child in self.children]
        content = "\n\n".join(content_parts)
        return f"::: column\n{content}\n:::"
