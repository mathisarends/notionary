from typing import Optional
from notionary.blocks.mappings.markdown_node import MarkdownNode


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

    def to_markdown(self) -> str:
        prefix = "+" + ("#" * self.level)
        result = f"{prefix} {self.text}"
        if self.content:
            result += "\n" + "\n".join([f"| {line}" for line in self.content])
        return result
