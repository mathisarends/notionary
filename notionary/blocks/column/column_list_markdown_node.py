from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode
from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode


class ColumnListMarkdownBlockParams(BaseModel):
    columns: list[ColumnMarkdownNode]
    model_config = {"arbitrary_types_allowed": True}


class ColumnListMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating a Markdown column list container.
    This represents the `::: columns` container that holds multiple columns
    with properly prefixed content.

    Example:
    ::: columns
    | ::: column
    | | Left content
    | | with double prefixed lines
    | :::
    |
    | ::: column 0.3
    | | Right content (30% width)
    | | with double prefixed lines
    | :::
    :::
    """

    def __init__(self, columns: list[ColumnMarkdownNode]):
        self.columns = columns

    @classmethod
    def from_params(
        cls, params: ColumnListMarkdownBlockParams
    ) -> ColumnListMarkdownNode:
        return cls(columns=params.columns)

    def to_markdown(self) -> str:
        if not self.columns:
            return "::: columns\n:::"

        column_parts = [column.to_markdown() for column in self.columns]
        columns_content = "\n\n".join(column_parts)

        lines = columns_content.split("\n")
        prefixed_lines = [f"| {line}" if line.strip() else "|" for line in lines]

        return "::: columns\n" + "\n".join(prefixed_lines) + "\n:::"
