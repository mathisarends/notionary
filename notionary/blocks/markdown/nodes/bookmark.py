from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.blocks.markdown.nodes.mixins.caption_markdown_node_mixin import CaptionMarkdownNodeMixin


class BookmarkMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced Bookmark node with Pydantic integration.
    Programmatic interface for creating Notion-style bookmark Markdown blocks.
    """

    url: str
    title: str | None = None
    caption: str | None = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [bookmark](https://example.com)
        - [bookmark](https://example.com)(caption:Some caption)
        """
        # Use simple bookmark syntax like BookmarkElement
        base_markdown = f"[bookmark]({self.url})"

        # Append caption using mixin helper
        return self.append_caption_to_markdown(base_markdown, self.caption)
