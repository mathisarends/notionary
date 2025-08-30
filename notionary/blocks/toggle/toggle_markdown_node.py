from notionary.blocks.markdown.markdown_node import MarkdownNode


class ToggleMarkdownNode(MarkdownNode):
    """
    Enhanced Toggle node with Pydantic integration.
    Clean programmatic interface for creating Notion-style Markdown toggle blocks
    with the simplified +++ "Title" syntax.

    Example:
        +++ "Advanced Details"
        Content here
        More content
        +++
    """

    title: str
    children: list[MarkdownNode] = []

    def to_markdown(self) -> str:
        result = f"+++ {self.title}"

        if not self.children:
            result += "\n+++"
            return result

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return result + "\n" + content_text + "\n+++"
