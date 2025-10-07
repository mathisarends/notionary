from typing import override

from notionary.blocks.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


class ColumnMarkdownNode(MarkdownNode):
    def __init__(
        self,
        children: list[MarkdownNode] | None = None,
        width_ratio: float | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.children = children or []
        self.width_ratio = width_ratio

    @override
    def to_markdown(self) -> str:
        column_syntax = self._syntax_registry.get_column_syntax()
        start_tag = (
            f"{column_syntax.start_delimiter} {self.width_ratio}"
            if self.width_ratio is not None
            else column_syntax.start_delimiter
        )

        if not self.children:
            return f"{start_tag}\n{column_syntax.end_delimiter}"

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return f"{start_tag}\n{content_text}\n{column_syntax.end_delimiter}"


class ColumnListMarkdownNode(MarkdownNode):
    def __init__(self, columns: list[ColumnMarkdownNode] | None = None, syntax_registry: SyntaxRegistry | None = None):
        super().__init__(syntax_registry=syntax_registry)
        self.columns = columns or []

    @override
    def to_markdown(self) -> str:
        column_list_syntax = self._syntax_registry.get_column_list_syntax()
        if not self.columns:
            return f"{column_list_syntax.start_delimiter}\n{column_list_syntax.end_delimiter}"

        column_parts = [column.to_markdown() for column in self.columns]
        columns_content = "\n\n".join(column_parts)

        return f"{column_list_syntax.start_delimiter}\n{columns_content}\n{column_list_syntax.end_delimiter}"
