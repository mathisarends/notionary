from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode
from notionary.markdown.markdown_document_model import MarkdownBlock
from notionary.markdown.markdown_node import MarkdownNode


class ColumnListMarkdownBlockParams(BaseModel):
    columns: list[list[MarkdownBlock]]
    width_ratios: Optional[list[float]] = None
    model_config = {"arbitrary_types_allowed": True}


class ColumnListMarkdownNode(MarkdownNode):
    """
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

        return f"::: columns\n{columns_content}\n:::"
