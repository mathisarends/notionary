from notionary.page.content.syntax import SyntaxDefinitionRegistry


class CaptionMarkdownNodeMixin:
    _syntax_registry: SyntaxDefinitionRegistry

    def _append_caption_to_markdown(self, base_markdown: str, caption: str | None) -> str:
        if not caption:
            return base_markdown

        caption_syntax = self._syntax_registry.get_caption_syntax()
        return f"{base_markdown}\n{caption_syntax.start_delimiter} {caption}"
