from notionary.blocks.mappings.markdown_node import MarkdownNode


class DividerMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown divider lines (---).
    """

    def to_markdown(self) -> str:
        return "---"
