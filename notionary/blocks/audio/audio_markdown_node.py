from notionary.blocks.markdown.markdown_node import MarkdownNode
from notionary.blocks.mixins.captions import CaptionMarkdownNodeMixin


class AudioMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    """
    Enhanced Audio node with Pydantic integration.
    Programmatic interface for creating Notion-style audio blocks.
    """

    url: str
    caption: str | None = None

    def to_markdown(self) -> str:
        """Return the Markdown representation.

        Examples:
        - [audio](https://example.com/song.mp3)
        - [audio](https://example.com/song.mp3)(caption:Background music)
        """
        base_markdown = f"[audio]({self.url})"
        return self.append_caption_to_markdown(base_markdown, self.caption)
