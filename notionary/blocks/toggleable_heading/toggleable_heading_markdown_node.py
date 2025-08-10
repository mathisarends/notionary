from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class ToggleableHeadingMarkdownBlockParams(BaseModel):
    text: str
    level: int
    children: list[MarkdownNode]
    model_config = {"arbitrary_types_allowed": True}


class ToggleableHeadingMarkdownNode(MarkdownNode):
    """
    Clean programmatic interface for creating collapsible Markdown headings (toggleable headings)
    with pipe-prefixed nested content using MarkdownNode children.

    Example:
        +## Advanced Section
        | ### Sub-heading
        |
        | Paragraph content with formatting
        |
        | | Column 1 | Column 2 |
        | |----------|----------|
        | | Data 1   | Data 2   |
        |
        | ```javascript
        | console.log("example");
        | ```
    """

    def __init__(self, text: str, level: int, children: list[MarkdownNode]):
        if not (1 <= level <= 3):
            raise ValueError("Only heading levels 1-3 are supported (H1, H2, H3)")
        self.text = text
        self.level = level
        self.children = children

    @classmethod
    def from_params(
        cls, params: ToggleableHeadingMarkdownBlockParams
    ) -> ToggleableHeadingMarkdownNode:
        return cls(text=params.text, level=params.level, children=params.children)

    def to_markdown(self) -> str:
        prefix = "+" + ("#" * self.level)
        result = f"{prefix} {self.text}"

        if not self.children:
            return result

        # Convert children to markdown and add toggle prefix
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        # Add toggle prefix to each line
        lines = content_text.split("\n")
        prefixed_lines = [f"| {line}" if line.strip() else "|" for line in lines]

        return result + "\n" + "\n".join(prefixed_lines)
