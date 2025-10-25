from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class TableMarkdownNode(MarkdownNode):
    def __init__(
        self, headers: list[str], rows: list[list[str]], syntax_registry: SyntaxDefinitionRegistry | None = None
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._validate_input(headers, rows)
        self.headers = headers
        self.rows = rows

    def _validate_input(self, headers: list[str], rows: list[list[str]]) -> None:
        if not headers:
            raise ValueError("headers must not be empty")
        if not all(isinstance(row, list) for row in rows):
            raise ValueError("rows must be a list of lists")

    @override
    def to_markdown(self) -> str:
        header = self._build_header_row()
        separator = self._build_separator_row()
        data_rows = self._build_data_rows()
        return "\n".join([header, separator, *data_rows])

    def _build_header_row(self) -> str:
        return self._format_row(self.headers)

    def _format_row(self, cells: list[str]) -> str:
        table_syntax = self._syntax_registry.get_table_syntax()
        delimiter = table_syntax.start_delimiter
        joined_cells = f" {delimiter} ".join(cells)
        return f"{delimiter} {joined_cells} {delimiter}"

    def _build_separator_row(self) -> str:
        table_syntax = self._syntax_registry.get_table_syntax()
        col_count = len(self.headers)
        separators = [table_syntax.end_delimiter] * col_count
        return self._format_row(separators)

    def _build_data_rows(self) -> list[str]:
        return [self._format_row(row) for row in self.rows]
