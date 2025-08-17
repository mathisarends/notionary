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
        # Use the correct +# syntax, not +++#
        prefix = "+" + ("#" * self.level)
        result = f"{prefix} {self.text}"

        if not self.children:
            return result

        # Convert children to markdown with pipe prefix for nested content
        content_parts = []
        for child in self.children:
            child_md = child.to_markdown()
            # Prefix each line with pipe
            prefixed_lines = ["| " + line for line in child_md.split("\n")]
            content_parts.append("\n".join(prefixed_lines))
        
        # Add empty pipe line between paragraphs
        content_text = "\n|\n".join(content_parts)

        return result + "\n" + content_text
