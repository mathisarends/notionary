from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class ColumnsMarkdownBlockParams(BaseModel):
    columns: list[list[str]]


class ColumnsMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating multi-column Markdown layouts using the custom Notion syntax.

    Example:
        ColumnsMarkdownBlock([
            ["## Column 1", "- Point A", "- Point B"],
            ["## Column 2", "- Point X", "- Point Y"]
        ]).to_markdown()
    """

    def __init__(self, columns: list[list[str]]):
        """
        Args:
            columns: List of columns, each column is a list of Markdown lines (as strings)
        """
        self.columns = columns

    @classmethod
    def from_params(cls, params: ColumnsMarkdownBlockParams) -> ColumnsMarkdownBlock:
        return cls(columns=params.columns)

    def to_markdown(self) -> str:
        """
        Converts the column layout to Notion-style Markdown.

        Returns:
            str: Markdown representation of the columns.
        """
        lines = ["::: columns"]
        for column_content in self.columns:
            lines.append("::: column")
            lines.extend(column_content)
            lines.append(":::")
        lines.append(":::")
        return "\n".join(lines)
