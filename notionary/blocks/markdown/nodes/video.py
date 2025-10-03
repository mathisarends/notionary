from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.blocks.markdown.nodes.mixins.caption_markdown_node_mixin import CaptionMarkdownNodeMixin


class VideoMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced Video node with Pydantic integration.
    Programmatic interface for creating Notion-style video blocks.
    """

    url: str
    caption: str | None = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [video](https://example.com/movie.mp4)
        - [video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)(caption:Music Video)
        """
        base_markdown = f"[video]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
