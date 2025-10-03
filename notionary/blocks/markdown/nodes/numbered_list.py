from notionary.blocks.markdown.nodes.base import MarkdownNode


class NumberedListMarkdownNode(MarkdownNode):
    """
    Enhanced NumberedList node with Pydantic integration.
    Programmatic interface for creating Markdown numbered list items.
    Example:
    1. First step
    2. Second step
    3. Third step
    """

    texts: list[str]

    def to_markdown(self) -> str:
        return "\n".join(f"{i + 1}. {text}" for i, text in enumerate(self.texts))
