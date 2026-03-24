from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.port import (
    RichTextHandler,
)
from notionary.rich_text.schemas import RichText, TextAnnotations


class TextHandler(RichTextHandler):
    def __init__(self, markdown_grammar: MarkdownGrammar):
        super().__init__(markdown_grammar)

    async def handle(self, rich_text: RichText) -> str:
        content = self._extract_plain_content(rich_text)
        return self._apply_text_formatting_to_content(rich_text, content)

    def _extract_plain_content(self, obj: RichText) -> str:
        if obj.plain_text:
            return obj.plain_text

        if obj.text:
            return obj.text.content

        return ""

    def _apply_text_formatting_to_content(self, obj: RichText, content: str) -> str:
        content = self._apply_link_formatting(obj, content)

        if not obj.annotations:
            return content

        # Note: Color formatting is handled at the converter level for proper grouping
        content = self._apply_inline_formatting(obj.annotations, content)

        return content

    def _apply_link_formatting(self, obj: RichText, content: str) -> str:
        if not (obj.text and obj.text.link):
            return content

        return (
            f"{self._markdown_grammar.link_prefix}"
            f"{content}"
            f"{self._markdown_grammar.link_middle}"
            f"{obj.text.link.url}"
            f"{self._markdown_grammar.link_suffix}"
        )

    def _apply_inline_formatting(
        self, annotations: TextAnnotations, content: str
    ) -> str:
        if annotations.code:
            content = self._wrap_with(content, self._markdown_grammar.code_wrapper)

        if annotations.strikethrough:
            content = self._wrap_with(
                content, self._markdown_grammar.strikethrough_wrapper
            )

        if annotations.italic:
            content = self._wrap_with(content, self._markdown_grammar.italic_wrapper)

        if annotations.underline:
            content = self._wrap_with(content, self._markdown_grammar.underline_wrapper)

        if annotations.bold:
            content = self._wrap_with(content, self._markdown_grammar.bold_wrapper)

        return content

    def _wrap_with(self, content: str, wrapper: str) -> str:
        return f"{wrapper}{content}{wrapper}"
