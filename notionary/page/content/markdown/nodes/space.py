from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class SpaceMarkdownNode(MarkdownNode):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry | None = None) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def to_markdown(self) -> str:
        space_syntax = self._syntax_registry.get_space_syntax()
        return space_syntax.start_delimiter
