from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode
from notionary.blocks.markdown.markdown_node import MarkdownNode


class ColumnListMarkdownNode(MarkdownNode):
    """
    Enhanced Column List node with Pydantic integration.
    Programmatic interface for creating a Markdown column list container.
    This represents the `::: columns` container that holds multiple columns.

    Example:
    ::: columns
    ::: column
    Left content
    with nested lines
    :::

    ::: column 0.3
    Right content (30% width)
    with nested lines
    :::
    :::
    """

    columns: list[ColumnMarkdownNode] = []

    def to_markdown(self) -> str:
        if not self.columns:
            return "::: columns\n:::"

        column_parts = [column.to_markdown() for column in self.columns]
        columns_content = "\n\n".join(column_parts)

        return f"::: columns\n{columns_content}\n:::"
