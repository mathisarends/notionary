from typing import Union
from notionary.blocks.mappings.markdown_node import MarkdownNode


class QuoteMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown blockquotes.
    Example:
        > This is a blockquote
        > that can span multiple lines
    """

    def __init__(self, text: Union[str, list[str]]):
        # Unterstützt String oder Liste von Strings (für mehrzeilige Quotes)
        if isinstance(text, list):
            self.lines = text
        else:
            self.lines = str(text).splitlines()  # Support für \n
        # Entferne führende/trailing spaces in jeder Zeile
        self.lines = [line.strip() for line in self.lines]

    def to_markdown(self) -> str:
        return "\n".join([f"> {line}" if line else ">" for line in self.lines])
