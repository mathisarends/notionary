from typing import override

from notionary.blocks.enums import CodeLanguage
from notionary.page.content.markdown.nodes.base import MarkdownNode
from notionary.page.content.markdown.nodes.mixins.caption import CaptionMarkdownNodeMixin
from notionary.page.content.syntax.service import SyntaxRegistry


class CodeMarkdownNode(MarkdownNode, CaptionMarkdownNodeMixin):
    def __init__(
        self,
        code: str,
        language: CodeLanguage | None = None,
        caption: str | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self.code = code
        self.language = language
        self.caption = caption

    @override
    def to_markdown(self) -> str:
        code_syntax = self._syntax_registry.get_code_syntax()
        lang = self.language or ""

        base_markdown = f"{code_syntax.start_delimiter}{lang}\n{self.code}\n{code_syntax.end_delimiter}"
        return self._append_caption_to_markdown(base_markdown, self.caption)
