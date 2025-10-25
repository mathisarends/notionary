from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.container import ContainerNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


class ColumnMarkdownNode(ContainerNode):
    def __init__(
        self,
        children: list[MarkdownNode] | None = None,
        width_ratio: float | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.children = children or []
        self.width_ratio = width_ratio

    @override
    def to_markdown(self) -> str:
        start_tag = self._format_column_start_tag()
        result = start_tag + self.render_children()
        return result

    def _format_column_start_tag(self) -> str:
        delimiter = self._syntax_registry.get_column_syntax().start_delimiter

        if self.width_ratio is not None:
            return f"{delimiter} {self.width_ratio}"
        return delimiter


class ColumnListMarkdownNode(MarkdownNode):
    def __init__(
        self,
        columns: list[ColumnMarkdownNode] | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.columns = columns or []

    @override
    def to_markdown(self) -> str:
        start_delimiter = self._get_column_list_delimiter()

        if not self.columns:
            return start_delimiter

        result = start_delimiter + self._render_columns()
        return result

    def _get_column_list_delimiter(self) -> str:
        return self._syntax_registry.get_column_list_syntax().start_delimiter

    def _render_columns(self) -> str:
        rendered_columns = []

        for column in self.columns:
            column_markdown = column.to_markdown()
            if column_markdown:
                indented = self._indent_column(column_markdown)
                rendered_columns.append(indented)

        return "\n" + "\n".join(rendered_columns) if rendered_columns else ""

    @staticmethod
    def _indent_column(text: str, indent: str = "    ") -> str:
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
