from notionary.blocks.markdown.nodes.base import MarkdownNode


class TableOfContentsMarkdownNode(MarkdownNode):
    """
    Enhanced Table of Contents node with Pydantic integration.
    Programmatic interface for creating Markdown table of contents blocks.
    Example:
    [toc]
    """

    def to_markdown(self) -> str:
        return "[toc]"
