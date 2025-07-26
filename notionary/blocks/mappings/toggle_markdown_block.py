from typing import Optional, List
from notionary.blocks.mappings.markdown_node import MarkdownNode


class ToggleMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown toggle blocks
    with pipe-prefixed nested content.
    Example:
        +++ Details
        | Here are the details.
        | You can add more lines.
    """

    def __init__(self, title: str, content: Optional[List[str]] = None):
        self.title = title
        # content: Optional[List[str]] — falls None, ist das ein leerer Toggle
        self.content = content or []

    def to_markdown(self) -> str:
        result = f"+++ {self.title}"
        if self.content:
            # Jede Zeile der content-Liste bekommt ein '| ' Prefix
            result += "\n" + "\n".join([f"| {line}" for line in self.content])
        return result
