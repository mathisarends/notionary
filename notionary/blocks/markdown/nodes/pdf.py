from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.blocks.markdown.nodes.mixins.caption_markdown_node_mixin import CaptionMarkdownNodeMixin


class PdfMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced PDF node with Pydantic integration.
    Programmatic interface for creating Notion-style PDF blocks.
    """

    url: str
    caption: str | None = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [pdf](https://example.com/document.pdf)
        - [pdf](https://example.com/document.pdf)(caption:Critical safety information)
        """
        base_markdown = f"[pdf]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
