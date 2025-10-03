from notionary.blocks.markdown.nodes.base import MarkdownNode


class SpaceMarkdownNode(MarkdownNode):
    """
    Enhanced Space node with Pydantic integration.
    Programmatic interface for creating Markdown space blocks using non-breaking space.
    """

    def to_markdown(self) -> str:
        return "[SPACE]"
