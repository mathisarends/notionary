from __future__ import annotations

from pydantic import Field

from notionary.markdown.markdown_node import MarkdownNode


class ToggleableHeadingMarkdownNode(MarkdownNode):
    """
    Enhanced Toggleable Heading node with Pydantic integration.
    Clean programmatic interface for creating collapsible Markdown headings (toggleable headings)
    with pipe-prefixed nested content using MarkdownNode children.

    Example syntax for a level-2 toggleable heading:
        +++## Advanced Section
        some content
        +++
    """

    text: str
    level: int = Field(ge=1, le=3)
    children: list[MarkdownNode] = Field(default_factory=list)

    def to_markdown(self) -> str:
        prefix = "+++" + ("#" * self.level)
        result = f"{prefix} {self.text}"

        if not self.children:
            result += "\n+++"
            return result

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return result + "\n" + content_text + "\n+++"