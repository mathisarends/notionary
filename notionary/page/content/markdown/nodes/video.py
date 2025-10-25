from typing import override

from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins.caption import CaptionMarkdownNodeMixin
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class VideoMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
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
        video_syntax = self._syntax_registry.get_video_syntax()
        base_markdown = f"{video_syntax.start_delimiter}{self.url}{video_syntax.end_delimiter}"
        return self._append_caption_to_markdown(base_markdown, self.caption)
