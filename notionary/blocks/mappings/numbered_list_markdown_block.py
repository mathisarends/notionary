from notionary.blocks.mappings.markdown_node import MarkdownNode


class NumberedListMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown numbered list items.
    Example: 1. First step
    """

    def __init__(self, text: str, number: int = 1):
        self.text = text
        self.number = number

    def to_markdown(self) -> str:
        return f"{self.number}. {self.text}"
