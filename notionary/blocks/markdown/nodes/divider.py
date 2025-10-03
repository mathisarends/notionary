from notionary.blocks.markdown.nodes.base import MarkdownNode


class DividerMarkdownNode(MarkdownNode):
    """
    Enhanced Divider node with Pydantic integration.
    Programmatic interface for creating Markdown divider lines (---).
    """

    def to_markdown(self) -> str:
        return "---"
