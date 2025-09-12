from notionary.blocks.markdown.markdown_node import MarkdownNode
from notionary.blocks.space.space_models import SPACE_MARKER


class SpaceMarkdownNode(MarkdownNode):
    """
    Enhanced Space node with Pydantic integration.
    Programmatic interface for creating Markdown space blocks using non-breaking space.
    """

    def to_markdown(self) -> str:
        return SPACE_MARKER
