from typing import Optional

from notionary.blocks.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class PdfMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced PDF node with Pydantic integration.
    Programmatic interface for creating Notion-style PDF blocks.
    """

    url: str
    caption: Optional[str] = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [pdf](https://example.com/document.pdf)
        - [pdf](https://example.com/document.pdf)(caption:Critical safety information)
        """
        base_markdown = f"[pdf]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
