from pydantic import Field

from notionary.blocks.markdown.nodes.base import MarkdownNode


class HeadingMarkdownNode(MarkdownNode):
    """
    Enhanced Heading node with Pydantic integration.
    Programmatic interface for creating Markdown headings (H1-H3).
    Example: # Heading 1, ## Heading 2, ### Heading 3
    """

    text: str
    level: int = Field(default=1, ge=1, le=3)

    def to_markdown(self) -> str:
        return f"{'#' * self.level} {self.text}"
