from notionary.blocks.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class ImageMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced Image node with Pydantic integration.
    Programmatic interface for creating Notion-style image blocks.
    """

    url: str
    caption: str | None = None
    alt: str | None = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [image](https://example.com/screenshot.png)
        - [image](https://example.com/screenshot.png)(caption:Dashboard overview)
        """
        base_markdown = f"[image]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
