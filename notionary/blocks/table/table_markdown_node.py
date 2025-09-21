from pydantic import field_validator

from notionary.blocks.markdown.markdown_node import MarkdownNode


class TableMarkdownNode(MarkdownNode):
    """
    Enhanced Table node with Pydantic integration.
    Programmatic interface for creating Markdown tables.
    Example:
        | Header 1 | Header 2 | Header 3 |
        | -------- | -------- | -------- |
        | Cell 1   | Cell 2   | Cell 3   |
        | Cell 4   | Cell 5   | Cell 6   |
    """

    headers: list[str]
    rows: list[list[str]]

    @field_validator("headers")
    @classmethod
    def validate_headers(cls, v):
        if not v:
            raise ValueError("headers must not be empty")
        return v

    @field_validator("rows")
    @classmethod
    def validate_rows(cls, v):
        if not all(isinstance(row, list) for row in v):
            raise ValueError("rows must be a list of lists")
        return v

    def to_markdown(self) -> str:
        col_count = len(self.headers)
        # Header row
        header = "| " + " | ".join(self.headers) + " |"
        # Separator row
        separator = "| " + " | ".join(["--------"] * col_count) + " |"
        # Data rows
        data_rows = ["| " + " | ".join(row) + " |" for row in self.rows]
        return "\n".join([header, separator, *data_rows])
