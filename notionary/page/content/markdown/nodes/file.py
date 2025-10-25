from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins.caption import CaptionMarkdownNodeMixin
from notionary.page.content.syntax import SyntaxDefinitionRegistry


class FileMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    def __init__(
        self,
        url: str,
        caption: str | None = None,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.url = url
        self.caption = caption

    @override
    def to_markdown(self) -> str:
        file_syntax = self._syntax_registry.get_file_syntax()
        base_markdown = f"{file_syntax.start_delimiter}{self.url}{file_syntax.end_delimiter}"
        return self._append_caption_to_markdown(base_markdown, self.caption)
