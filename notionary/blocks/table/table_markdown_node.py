from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class TableMarkdownBlockParams(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class TableMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown tables.
    Example:
        | Header 1 | Header 2 | Header 3 |
        | -------- | -------- | -------- |
        | Cell 1   | Cell 2   | Cell 3   |
        | Cell 4   | Cell 5   | Cell 6   |
    """

    def __init__(self, headers: list[str], rows: list[list[str]]):
        if not headers or not all(isinstance(row, list) for row in rows):
            raise ValueError("headers must be a list and rows must be a list of lists")
        self.headers = headers
        self.rows = rows

    @classmethod
    def from_params(cls, params: TableMarkdownBlockParams) -> TableMarkdownNode:
        return cls(headers=params.headers, rows=params.rows)

    def to_markdown(self) -> str:
        col_count = len(self.headers)
        # Header row
        header = "| " + " | ".join(self.headers) + " |"
        # Separator row
        separator = "| " + " | ".join(["--------"] * col_count) + " |"
        # Data rows
        data_rows = ["| " + " | ".join(row) + " |" for row in self.rows]
        return "\n".join([header, separator] + data_rows)
