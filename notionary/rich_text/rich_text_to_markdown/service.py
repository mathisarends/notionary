from dataclasses import dataclass
from typing import ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.schemas import (
    MentionDate,
    MentionType,
    RichText,
    RichTextType,
    TextAnnotations,
)
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    NameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
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
        page_resolver: NameIdResolver | None = None,
        database_resolver: NameIdResolver | None = None,
        data_source_resolver: NameIdResolver | None = None,
        person_resolver: NameIdResolver | None = None,
        markdown_grammar: MarkdownGrammar | None = None,
    ) -> None:
        self.page_resolver = page_resolver or PageNameIdResolver()
        self.database_resolver = database_resolver or DatabaseNameIdResolver()
        self.data_source_resolver = data_source_resolver or DataSourceNameIdResolver()
        self.person_resolver = person_resolver or PersonNameIdResolver()
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()

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
        mention_markdown = await self._extract_mention_markdown(obj)
        return mention_markdown if mention_markdown else ""

    def _extract_plain_content(self, obj: RichText) -> str:
        if obj.plain_text:
            return obj.plain_text

        if obj.text:
            return obj.text.content

        return ""

    async def _extract_mention_markdown(self, obj: RichText) -> str | None:
        if not obj.mention:
            return None

        mention = obj.mention

        if mention.type == MentionType.PAGE and mention.page:
            return await self._extract_page_mention_markdown(mention.page.id)

        if mention.type == MentionType.DATABASE and mention.database:
            return await self._extract_database_mention_markdown(mention.database.id)

        if mention.type == MentionType.DATASOURCE and mention.data_source:
            return await self._extract_data_source_mention_markdown(
                mention.data_source.id
            )

        if mention.type == MentionType.USER and mention.user:
            return await self._extract_user_mention_markdown(mention.user.id)

        if mention.type == MentionType.DATE and mention.date:
            return self._extract_date_mention_markdown(mention.date)

        return None

    async def _extract_page_mention_markdown(self, page_id: str) -> str:
        page_name = await self.page_resolver.resolve_id_to_name(page_id)
        return self._format_mention(
            self._markdown_grammar.page_mention_prefix, page_name or page_id
        )

    async def _extract_database_mention_markdown(self, database_id: str) -> str:
        database_name = await self.database_resolver.resolve_id_to_name(database_id)
        return self._format_mention(
            self._markdown_grammar.database_mention_prefix, database_name or database_id
        )

    async def _extract_data_source_mention_markdown(self, data_source_id: str) -> str:
        data_source_name = await self.data_source_resolver.resolve_id_to_name(
            data_source_id
        )
        return self._format_mention(
            self._markdown_grammar.datasource_mention_prefix,
            data_source_name or data_source_id,
        )

    async def _extract_user_mention_markdown(self, user_id: str) -> str:
        user_name = await self.person_resolver.resolve_id_to_name(user_id)
        return self._format_mention(
            self._markdown_grammar.user_mention_prefix, user_name or user_id
        )

    def _format_mention(self, prefix: str, name: str) -> str:
        return f"{prefix}{name}{self._markdown_grammar.mention_suffix}"

    def _extract_date_mention_markdown(self, date_mention: MentionDate) -> str:
        date_range = self._format_date_range(date_mention)
        return self._format_mention(
            self._markdown_grammar.date_mention_prefix, date_range
        )

    def _format_date_range(self, date_mention: MentionDate) -> str:
        if date_mention.end:
            return f"{date_mention.start}–{date_mention.end}"

        return date_mention.start

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
