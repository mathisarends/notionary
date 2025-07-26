from typing import Optional
from notionary.blocks.mappings.markdown_node import MarkdownNode


class ImageMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown image blocks.
    Supports optional caption and alt text.
    Example: ![Caption](https://example.com/image.jpg "alt text")
    """

    def __init__(
        self, url: str, caption: Optional[str] = None, alt: Optional[str] = None
    ):
        self.url = url
        self.caption = caption or ""
        self.alt = alt

    def to_markdown(self) -> str:
        if self.alt:
            return f'![{self.caption}]({self.url} "{self.alt}")'
        return f"![{self.caption}]({self.url})"
