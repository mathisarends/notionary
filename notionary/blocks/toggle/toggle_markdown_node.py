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
    with the simplified +++ "Title" syntax.

    Example:
        +++ "Advanced Details"
        Content here
        More content
        +++
    """

    def __init__(self, title: str, children: list[MarkdownNode]):
        self.title = title
        self.children = children

    @classmethod
    def from_params(cls, params: ToggleMarkdownBlockParams) -> ToggleMarkdownNode:
        return cls(title=params.title, children=params.children)

    def to_markdown(self) -> str:
        # ✅ Updated to new simplified syntax
        result = f'+++ "{self.title}"'

        if not self.children:
            result += "\n+++"
            return result

        # Convert children to markdown 
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return result + "\n" + content_text + "\n+++"