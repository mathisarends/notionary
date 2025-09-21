from pydantic import Field

from notionary.blocks.markdown.markdown_node import MarkdownNode


class ColumnMarkdownNode(MarkdownNode):
    """
    Example:
        ::: column
        # Column Title

        Some content here
        :::

        ::: column 0.7
        # Wide Column (70%)

        This column takes 70% width
        :::
    """

    children: list[MarkdownNode] = Field(default_factory=list)
    width_ratio: float | None = None

    def to_markdown(self) -> str:
        start_tag = f"::: column {self.width_ratio}" if self.width_ratio is not None else "::: column"

        if not self.children:
            return f"{start_tag}\n:::"

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return f"{start_tag}\n{content_text}\n:::"
