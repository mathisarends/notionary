from __future__ import annotations

from notionary.page.content.markdown.builder import MarkdownBuilder
from notionary.page.content.markdown.structured_output.models import (
    AudioSchema,
    BookmarkSchema,
    BreadcrumbSchema,
    BulletedListItemSchema,
    BulletedListSchema,
    CalloutSchema,
    CodeSchema,
    ColumnsSchema,
    EmbedSchema,
    EquationSchema,
    FileSchema,
    HeadingSchema,
    ImageSchema,
    MarkdownDocumentSchema,
    MarkdownNodeSchema,
    MermaidSchema,
    NumberedListItemSchema,
    NumberedListSchema,
    ParagraphSchema,
    PdfSchema,
    QuoteSchema,
    TableOfContentsSchema,
    TableSchema,
    TodoListSchema,
    TodoSchema,
    ToggleSchema,
    VideoSchema,
)
from notionary.utils.mixins.logging import LoggingMixin


class StructuredOutputMarkdownConverter(LoggingMixin):
    def __init__(self, builder: MarkdownBuilder | None = None) -> None:
        self.builder = builder or MarkdownBuilder()

    def convert(self, schema: MarkdownDocumentSchema) -> str:
        for node in schema.nodes:
            self._process_node(node)
        return self.builder.build()

    def _process_node(self, node: MarkdownNodeSchema) -> None:
        node.process_with(self)

    def _process_heading(self, node: HeadingSchema) -> None:
        builder_func = (
            self._create_children_builder(node.children) if node.children else None
        )

        if node.level == 1:
            self.builder.h1(node.text, builder_func)
        elif node.level == 2:
            self.builder.h2(node.text, builder_func)
        elif node.level == 3:
            self.builder.h3(node.text, builder_func)

    def _process_paragraph(self, node: ParagraphSchema) -> None:
        self.builder.paragraph(node.text)

    def _process_space(self) -> None:
        self.builder.space()

    def _process_divider(self) -> None:
        self.builder.divider()

    def _process_quote(self, node: QuoteSchema) -> None:
        builder_func = (
            self._create_children_builder(node.children) if node.children else None
        )
        self.builder.quote(node.text, builder_func)

    def _process_bulleted_list(self, node: BulletedListSchema) -> None:
        self.builder.bulleted_list(node.items)

    def _process_bulleted_list_item(self, node: BulletedListItemSchema) -> None:
        builder_func = (
            self._create_children_builder(node.children) if node.children else None
        )
        self.builder.bulleted_list_item(node.text, builder_func)

    def _process_numbered_list(self, node: NumberedListSchema) -> None:
        self.builder.numbered_list(node.items)

    def _process_numbered_list_item(self, node: NumberedListItemSchema) -> None:
        builder_func = (
            self._create_children_builder(node.children) if node.children else None
        )
        self.builder.numbered_list_item(node.text, builder_func)

    def _process_todo(self, node: TodoSchema) -> None:
        builder_func = (
            self._create_children_builder(node.children) if node.children else None
        )
        self.builder.todo(node.text, checked=node.checked, builder_func=builder_func)

    def _process_todo_list(self, node: TodoListSchema) -> None:
        self.builder.todo_list(node.items, node.completed)

    def _process_callout(self, node: CalloutSchema) -> None:
        if node.children:
            builder_func = self._create_children_builder(node.children)
            self.builder.callout_with_children(node.text, node.emoji, builder_func)
        else:
            self.builder.callout(node.text, node.emoji)

    def _process_toggle(self, node: ToggleSchema) -> None:
        builder_func = self._create_children_builder(node.children)
        self.builder.toggle(node.title, builder_func)

    def _process_image(self, node: ImageSchema) -> None:
        self.builder.image(node.url, node.caption)

    def _process_video(self, node: VideoSchema) -> None:
        self.builder.video(node.url, node.caption)

    def _process_audio(self, node: AudioSchema) -> None:
        self.builder.audio(node.url, node.caption)

    def _process_file(self, node: FileSchema) -> None:
        self.builder.file(node.url, node.caption)

    def _process_pdf(self, node: PdfSchema) -> None:
        self.builder.pdf(node.url, node.caption)

    def _process_bookmark(self, node: BookmarkSchema) -> None:
        self.builder.bookmark(node.url, node.title, node.caption)

    def _process_embed(self, node: EmbedSchema) -> None:
        self.builder.embed(node.url, node.caption)

    def _process_code(self, node: CodeSchema) -> None:
        self.builder.code(node.code, node.language, node.caption)

    def _process_mermaid(self, node: MermaidSchema) -> None:
        self.builder.mermaid(node.diagram, node.caption)

    def _process_table(self, node: TableSchema) -> None:
        self.builder.table(node.headers, node.rows)

    def _process_breadcrumb(self, node: BreadcrumbSchema) -> None:
        self.builder.breadcrumb()

    def _process_equation(self, node: EquationSchema) -> None:
        self.builder.equation(node.expression)

    def _process_table_of_contents(self, node: TableOfContentsSchema) -> None:
        self.builder.table_of_contents()

    def _process_columns(self, node: ColumnsSchema) -> None:
        builder_funcs = []
        width_ratios = []

        for column in node.columns:
            builder_func = self._create_children_builder(column.children)
            builder_funcs.append(builder_func)
            width_ratios.append(column.width_ratio)

        if any(r is not None for r in width_ratios):
            self.builder.columns(*builder_funcs, width_ratios=width_ratios)
        else:
            self.builder.columns(*builder_funcs)

    def _create_children_builder(self, children: list[MarkdownNodeSchema] | None):
        if not children:
            return None

        captured_children = children

        def builder_func(builder: MarkdownBuilder) -> MarkdownBuilder:
            converter = StructuredOutputMarkdownConverter()
            converter.builder = builder
            for child in captured_children:
                converter._process_node(child)
            return builder

        return builder_func
