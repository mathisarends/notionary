from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins import ChildrenRenderMixin
from notionary.page.content.syntax import SyntaxRegistry


class NumberedListMarkdownNode(ChildrenRenderMixin, MarkdownNode):
    def __init__(
        self,
        texts: list[str],
        children: list[MarkdownNode | None] | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ):
        super().__init__(syntax_registry=syntax_registry)
        self.texts = texts
        self.children = children or []

    @override
    def to_markdown(self) -> str:
        list_items = [self._render_list_item(index, text) for index, text in enumerate(self.texts)]
        return "\n".join(list_items)

    def _render_list_item(self, index: int, text: str) -> str:
        item_number = index + 1
        item_line = f"{item_number}. {text}"

        child = self._get_child_for_item(index)
        if child:
            child_content = self.render_child(child)
            return f"{item_line}\n{child_content}"

        return item_line

    def _get_child_for_item(self, index: int) -> MarkdownNode | None:
        if not self.children or index >= len(self.children):
            return None
        return self.children[index]
