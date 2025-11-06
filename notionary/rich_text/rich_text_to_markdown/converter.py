from typing import ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.color_chunker import (
    ColorGroup,
    chunk_by_color,
)
from notionary.rich_text.rich_text_to_markdown.handlers.registry import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.schemas import RichText, TextAnnotations
from notionary.utils.mixins.logging import LoggingMixin


class RichTextToMarkdownConverter(LoggingMixin):
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(
        self,
        markdown_grammar: MarkdownGrammar,
        rich_text_handler_registry: RichTextHandlerRegistry,
    ) -> None:
        self._markdown_grammar = markdown_grammar
        self._rich_text_handler_registry = rich_text_handler_registry

    async def to_markdown(self, rich_text: list[RichText]) -> str:
        if not rich_text:
            return ""

        color_groups = chunk_by_color(rich_text)
        markdown_parts = await self._convert_groups_to_markdown(color_groups)

        return "".join(markdown_parts)

    async def _convert_groups_to_markdown(self, groups: list[ColorGroup]) -> list[str]:
        return [await self._convert_group_to_markdown(group) for group in groups]

    async def _convert_group_to_markdown(self, group: ColorGroup) -> str:
        if self._should_apply_color(group.color):
            return await self._convert_colored_group(group)
        return await self._convert_uncolored_group(group)

    def _should_apply_color(self, color: BlockColor) -> bool:
        return color != BlockColor.DEFAULT and color.value in self.VALID_COLORS

    async def _convert_colored_group(self, group: ColorGroup) -> str:
        inner_parts = await self._convert_rich_texts_without_color(group.objects)
        combined_content = "".join(inner_parts)
        return self._wrap_with_color(combined_content, group.color)

    async def _convert_uncolored_group(self, group: ColorGroup) -> str:
        parts = await self._convert_rich_texts_with_color(group.objects)
        return "".join(parts)

    async def _convert_rich_texts_without_color(
        self, objects: list[RichText]
    ) -> list[str]:
        return [
            await self._convert_rich_text_to_markdown(obj, skip_color=True)
            for obj in objects
        ]

    async def _convert_rich_texts_with_color(
        self, objects: list[RichText]
    ) -> list[str]:
        return [await self._convert_rich_text_to_markdown(obj) for obj in objects]

    async def _convert_rich_text_to_markdown(
        self, obj: RichText, skip_color: bool = False
    ) -> str:
        handler = self._get_handler_for(obj)
        if not handler:
            return ""

        result = await handler.handle(obj)

        if self._should_apply_color_to_result(obj, skip_color):
            result = self._apply_color_formatting(obj.annotations, result)

        return result

    def _get_handler_for(self, obj: RichText):
        handler = self._rich_text_handler_registry.get_handler(obj.type)
        if not handler:
            self.logger.warning(
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
