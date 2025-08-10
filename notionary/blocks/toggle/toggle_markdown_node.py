from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class ToggleMarkdownBlockParams(BaseModel):
    title: str
    children: list[MarkdownNode]
    model_config = {"arbitrary_types_allowed": True}


class ToggleMarkdownNode(MarkdownNode):
    """
    Clean programmatic interface for creating Notion-style Markdown toggle blocks
    with pipe-prefixed nested content using MarkdownNode children.

    Example:
        +++ Advanced Details
        | ## Subheading
        |
        | Paragraph with **bold** text
        |
        | - list item 1
        | - list item 2
        |
        | ```python
        | print("code example")
        | ```
    """

    def __init__(self, title: str, children: list[MarkdownNode]):
        self.title = title
        self.children = children

    @classmethod
    def from_params(cls, params: ToggleMarkdownBlockParams) -> ToggleMarkdownNode:
        return cls(title=params.title, children=params.children)

    def to_markdown(self) -> str:
        result = f"+++ {self.title}"

        if not self.children:
            return result

        # Convert children to markdown and add toggle prefix
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        # Add toggle prefix to each line
        lines = content_text.split("\n")
        prefixed_lines = [f"| {line}" if line.strip() else "|" for line in lines]

        return result + "\n" + "\n".join(prefixed_lines)
