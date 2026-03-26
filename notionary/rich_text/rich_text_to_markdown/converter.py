import logging
from typing import ClassVar

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.color_chunker import (
    ColorGroup,
    chunk_by_color,
)
from notionary.rich_text.rich_text_to_markdown.handlers.inline_equation import (
    EquationHandler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handler import (
    MentionRichTextHandler,
)
from notionary.rich_text.rich_text_to_markdown.handlers.port import RichTextHandler
from notionary.rich_text.rich_text_to_markdown.handlers.text import TextHandler
from notionary.rich_text.schemas import (
    BlockColor,
    RichText,
    RichTextType,
    TextAnnotations,
)

logger = logging.getLogger(__name__)


class RichTextToMarkdownConverter:
    _VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(self) -> None:
        self._markdown_grammar = MarkdownGrammar()
        self._handlers: dict[RichTextType, RichTextHandler] = {
            RichTextType.TEXT: TextHandler(),
            RichTextType.EQUATION: EquationHandler(),
            RichTextType.MENTION: MentionRichTextHandler(),
        }

    def convert(self, rich_text: list[RichText]) -> str:
        if not rich_text:
            return ""

        color_groups = chunk_by_color(rich_text)
        markdown_parts = self._convert_groups_to_markdown(color_groups)

        return "".join(markdown_parts)

    def _convert_groups_to_markdown(self, groups: list[ColorGroup]) -> list[str]:
        return [self._convert_group_to_markdown(group) for group in groups]

    def _convert_group_to_markdown(self, group: ColorGroup) -> str:
        if self._should_apply_color(group.color):
            return self._convert_colored_group(group)
        return self._convert_uncolored_group(group)

    def _should_apply_color(self, color: BlockColor) -> bool:
        return color != BlockColor.DEFAULT and color.value in self._VALID_COLORS

    def _convert_colored_group(self, group: ColorGroup) -> str:
        inner_parts = self._convert_rich_texts_without_color(group.objects)
        combined_content = "".join(inner_parts)
        return self._wrap_with_color(combined_content, group.color)

    def _convert_uncolored_group(self, group: ColorGroup) -> str:
        parts = self._convert_rich_texts_with_color(group.objects)
        return "".join(parts)

    def _convert_rich_texts_without_color(self, objects: list[RichText]) -> list[str]:
        return [
            self._convert_rich_text_to_markdown(obj, skip_color=True) for obj in objects
        ]

    def _convert_rich_texts_with_color(self, objects: list[RichText]) -> list[str]:
        return [self._convert_rich_text_to_markdown(obj) for obj in objects]

    def _convert_rich_text_to_markdown(
        self, obj: RichText, skip_color: bool = False
    ) -> str:
        handler = self._get_handler_for(obj)
        if not handler:
            return ""

        result = handler.handle(obj)

        if self._should_apply_color_to_result(obj, skip_color):
            result = self._apply_color_formatting(obj.annotations, result)

        return result

    def _get_handler_for(self, obj: RichText) -> RichTextHandler | None:
        handler = self._handlers.get(obj.type)
        if not handler:
            logger.warning(
                f"No handler found for rich text type: {obj.type}. Skipping."
            )
        return handler

    def _should_apply_color_to_result(self, obj: RichText, skip_color: bool) -> bool:
        return not skip_color and obj.annotations is not None

    def _apply_color_formatting(
        self, annotations: TextAnnotations, content: str
    ) -> str:
        if not self._has_valid_color(annotations):
            return content
        return self._wrap_with_color(content, annotations.color)

    def _has_valid_color(self, annotations: TextAnnotations) -> bool:
        if annotations.color is None:
            return False
        return self._should_apply_color(annotations.color)

    def _wrap_with_color(self, content: str, color: BlockColor) -> str:
        base_color = color.get_base_color()

        if color.is_background():
            return self._wrap_with_background_color(content, base_color)
        return self._wrap_with_foreground_color(content, base_color)

    def _wrap_with_background_color(self, content: str, base_color: str) -> str:
        wrapper = self._markdown_grammar.background_color_wrapper
        return f"{wrapper}{{{base_color}}}{content}{wrapper}"

    def _wrap_with_foreground_color(self, content: str, base_color: str) -> str:
        return f"{{{base_color}}}{content}"
