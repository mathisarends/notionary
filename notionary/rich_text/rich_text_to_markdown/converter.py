from dataclasses import dataclass
from typing import ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.mentions.registry import (
    MentionHandlerRegistryFactory,
)
from notionary.rich_text.rich_text_to_markdown.mentions.registry.service import (
    MentionHandlerRegistry,
)
from notionary.rich_text.schemas import (
    RichText,
    RichTextType,
    TextAnnotations,
)


@dataclass
class ColorGroup:
    color: BlockColor
    objects: list[RichText]


class RichTextToMarkdownConverter:
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(
        self,
        *,
        markdown_grammar: MarkdownGrammar | None = None,
        mention_handler_registry: MentionHandlerRegistry | None = None,
    ) -> None:
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()
        if mention_handler_registry is None:
            factory = MentionHandlerRegistryFactory(self._markdown_grammar)
            mention_handler_registry = factory.create()
        self._mention_handler_registry = mention_handler_registry

    async def to_markdown(self, rich_text: list[RichText]) -> str:
        if not rich_text:
            return ""

        color_groups = self._group_by_color(rich_text)
        markdown_parts = [
            await self._convert_group_to_markdown(group) for group in color_groups
        ]

        return "".join(markdown_parts)

    def _group_by_color(self, rich_text: list[RichText]) -> list[ColorGroup]:
        if not rich_text:
            return []

        groups: list[ColorGroup] = []
        current_color = (
            rich_text[0].annotations.color
            if rich_text[0].annotations
            else BlockColor.DEFAULT
        )
        current_group: list[RichText] = []

        for obj in rich_text:
            obj_color = obj.annotations.color if obj.annotations else BlockColor.DEFAULT

            if obj_color == current_color:
                current_group.append(obj)
            else:
                groups.append(ColorGroup(color=current_color, objects=current_group))
                current_color = obj_color
                current_group = [obj]

        groups.append(ColorGroup(color=current_color, objects=current_group))
        return groups

    async def _convert_group_to_markdown(self, group: ColorGroup) -> str:
        if self._should_apply_color(group.color):
            return await self._convert_colored_group(group)

        return await self._convert_uncolored_group(group)

    def _should_apply_color(self, color: BlockColor) -> bool:
        return color != BlockColor.DEFAULT and color.value in self.VALID_COLORS

    async def _convert_colored_group(self, group: ColorGroup) -> str:
        inner_parts = [
            await self._convert_rich_text_to_markdown(obj, skip_color=True)
            for obj in group.objects
        ]
        combined_content = "".join(inner_parts)
        return self._wrap_with_color(combined_content, group.color)

    async def _convert_uncolored_group(self, group: ColorGroup) -> str:
        parts = [
            await self._convert_rich_text_to_markdown(obj) for obj in group.objects
        ]
        return "".join(parts)

    def _wrap_with_color(self, content: str, color: BlockColor) -> str:
        base_color = color.get_base_color()

        if color.is_background():
            return f"=={{{base_color}}}{content}=="

        return f"{{{base_color}}}{content}"

    async def _convert_rich_text_to_markdown(
        self, obj: RichText, skip_color: bool = False
    ) -> str:
        if obj.type == RichTextType.EQUATION and obj.equation:
            return self._convert_equation(obj)

        if obj.type == RichTextType.MENTION:
            return await self._convert_mention(obj)

        content = self._extract_plain_content(obj)
        return self._apply_text_formatting_to_content(obj, content, skip_color)

    def _convert_equation(self, obj: RichText) -> str:
        return f"{self._markdown_grammar.inline_equation_wrapper}{obj.equation.expression}{self._markdown_grammar.inline_equation_wrapper}"

    async def _convert_mention(self, obj: RichText) -> str:
        if not obj.mention:
            return ""

        mention = obj.mention
        handler = self._mention_handler_registry.get_handler(mention.type)

        if not handler:
            return ""

        return await handler.handle(mention)

    def _extract_plain_content(self, obj: RichText) -> str:
        if obj.plain_text:
            return obj.plain_text

        if obj.text:
            return obj.text.content

        return ""

    def _apply_text_formatting_to_content(
        self, obj: RichText, content: str, skip_color: bool = False
    ) -> str:
        content = self._apply_link_formatting(obj, content)

        if not obj.annotations:
            return content

        content = self._apply_inline_formatting(obj.annotations, content)

        if not skip_color:
            content = self._apply_color_formatting(obj.annotations, content)

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

    def _apply_color_formatting(
        self, annotations: TextAnnotations, content: str
    ) -> str:
        if not self._should_apply_color(annotations.color):
            return content

        return self._wrap_with_color(content, annotations.color)

    def _wrap_with(self, content: str, wrapper: str) -> str:
        return f"{wrapper}{content}{wrapper}"
