from typing import override

from notionary.markdown.nodes.base import MarkdownNode
from notionary.markdown.nodes.mixins.caption import CaptionMarkdownNodeMixin
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


class ImageMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
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
        image_syntax = self._syntax_registry.get_image_syntax()
        base_markdown = (
            f"{image_syntax.start_delimiter}{self.url}{image_syntax.end_delimiter}"
        )
        return self._append_caption_to_markdown(base_markdown, self.caption)
