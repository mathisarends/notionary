from pydantic import Field

from notionary.blocks.markdown.nodes.base import MarkdownNode


class CalloutMarkdownNode(MarkdownNode):
    """
    Enhanced Callout node with Pydantic integration.
    Programmatic interface for creating Notion-style callout Markdown blocks.
    Example:
        ::: callout
        This is important
        :::

        ::: callout ⚠️
        This is important with emoji
        :::
    """

    text: str
    emoji: str | None = None
    children: list[MarkdownNode] = Field(default_factory=list)

    def to_markdown(self) -> str:
        start_tag = f"::: callout {self.emoji}" if self.emoji else "::: callout"

        if not self.children:
            return f"{start_tag}\n{self.text}\n:::"

        # Convert children to markdown
        content_parts = [self.text] + [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return f"{start_tag}\n{content_text}\n:::"
