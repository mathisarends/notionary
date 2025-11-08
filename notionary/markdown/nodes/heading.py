from typing import override

from notionary.markdown.nodes.base import MarkdownNode
from notionary.markdown.nodes.container import ContainerNode
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


class HeadingMarkdownNode(ContainerNode):
    MIN_LEVEL = 1
    MAX_LEVEL = 3

    def __init__(
        self,
        text: str,
        level: int = 1,
        children: list[MarkdownNode] | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.text = text
        self.level = self._validate_level(level)
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        heading_prefix = self._get_heading_prefix()
        result = f"{heading_prefix} {self.text}"
        result += self.render_children()
        return result

    def _validate_level(self, level: int) -> int:
        return max(self.MIN_LEVEL, min(self.MAX_LEVEL, level))

    def _get_heading_prefix(self) -> str:
        delimiter = self._syntax_registry.get_heading_syntax().start_delimiter
        return delimiter * self.level
