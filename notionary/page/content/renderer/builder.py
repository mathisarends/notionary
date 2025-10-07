from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.page.content.renderer.renderers import (
    AudioRenderer,
    BlockRenderer,
    BookmarkRenderer,
    BreadcrumbRenderer,
    BulletedListRenderer,
    CalloutRenderer,
    CodeRenderer,
    ColumnListRenderer,
    ColumnRenderer,
    DividerRenderer,
    EmbedRenderer,
    EquationRenderer,
    FallbackRenderer,
    FileRenderer,
    HeadingRenderer,
    ImageRenderer,
    NumberedListRenderer,
    ParagraphRenderer,
    PdfRenderer,
    QuoteRenderer,
    TableOfContentsRenderer,
    TableRenderer,
    TableRowHandler,
    TodoRenderer,
    ToggleableHeadingRenderer,
    ToggleRenderer,
    VideoRenderer,
)
from notionary.page.content.syntax.service import SyntaxRegistry


# TODO: This is unused for now however we want to use this to make this more testable
class RendererChainFactory:
    def __init__(
        self,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ) -> None:
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()
        self._syntax_registry = syntax_registry or SyntaxRegistry()

    def create(self) -> BlockRenderer:
        # Strukturelle Blocks
        toggle_handler = self._create_toggle_renderer()
        toggleable_heading_handler = self._create_toggleable_heading_renderer()
        heading_handler = self._create_heading_renderer()

        # Content Blocks
        callout_handler = self._create_callout_renderer()
        code_handler = self._create_code_renderer()
        quote_handler = self._create_quote_renderer()
        todo_handler = self._create_todo_renderer()
        bulleted_list_handler = self._create_bulleted_list_renderer()

        # Layout Blocks
        divider_handler = self._create_divider_renderer()
        column_list_handler = self._create_column_list_renderer()
        column_handler = self._create_column_renderer()
        numbered_list_handler = self._create_numbered_list_renderer()

        # Media Blocks
        bookmark_handler = self._create_bookmark_renderer()
        image_handler = self._create_image_renderer()
        video_handler = self._create_video_renderer()
        audio_handler = self._create_audio_renderer()
        file_handler = self._create_file_renderer()
        pdf_handler = self._create_pdf_renderer()
        embed_handler = self._create_embed_renderer()

        # Special Blocks
        equation_handler = self._create_equation_renderer()
        table_of_contents_handler = self._create_table_of_contents_renderer()
        breadcrumb_handler = self._create_breadcrumb_renderer()
        table_handler = self._create_table_renderer()
        table_row_handler = self._create_table_row_handler()

        # Standard & Fallback
        paragraph_handler = self._create_paragraph_renderer()
        fallback_handler = self._create_fallback_renderer()

        # Chain verketten - most specific first, fallback last
        (
            toggle_handler.set_next(toggleable_heading_handler)
            .set_next(heading_handler)
            .set_next(callout_handler)
            .set_next(code_handler)
            .set_next(quote_handler)
            .set_next(todo_handler)
            .set_next(bulleted_list_handler)
            .set_next(divider_handler)
            .set_next(column_list_handler)
            .set_next(column_handler)
            .set_next(numbered_list_handler)
            .set_next(bookmark_handler)
            .set_next(image_handler)
            .set_next(video_handler)
            .set_next(audio_handler)
            .set_next(file_handler)
            .set_next(pdf_handler)
            .set_next(embed_handler)
            .set_next(equation_handler)
            .set_next(table_of_contents_handler)
            .set_next(breadcrumb_handler)
            .set_next(table_handler)
            .set_next(table_row_handler)
            .set_next(paragraph_handler)
            .set_next(fallback_handler)
        )

        return toggle_handler

    # Renderer Creation Methods
    def _create_toggle_renderer(self) -> ToggleRenderer:
        return ToggleRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_toggleable_heading_renderer(self) -> ToggleableHeadingRenderer:
        return ToggleableHeadingRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_heading_renderer(self) -> HeadingRenderer:
        return HeadingRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_callout_renderer(self) -> CalloutRenderer:
        return CalloutRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_code_renderer(self) -> CodeRenderer:
        return CodeRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_quote_renderer(self) -> QuoteRenderer:
        return QuoteRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_todo_renderer(self) -> TodoRenderer:
        return TodoRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_bulleted_list_renderer(self) -> BulletedListRenderer:
        return BulletedListRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_divider_renderer(self) -> DividerRenderer:
        return DividerRenderer(syntax_registry=self._syntax_registry)

    def _create_column_list_renderer(self) -> ColumnListRenderer:
        return ColumnListRenderer(syntax_registry=self._syntax_registry)

    def _create_column_renderer(self) -> ColumnRenderer:
        return ColumnRenderer(syntax_registry=self._syntax_registry)

    def _create_numbered_list_renderer(self) -> NumberedListRenderer:
        return NumberedListRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_bookmark_renderer(self) -> BookmarkRenderer:
        return BookmarkRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_image_renderer(self) -> ImageRenderer:
        return ImageRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_video_renderer(self) -> VideoRenderer:
        return VideoRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_audio_renderer(self) -> AudioRenderer:
        return AudioRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_file_renderer(self) -> FileRenderer:
        return FileRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_pdf_renderer(self) -> PdfRenderer:
        return PdfRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_embed_renderer(self) -> EmbedRenderer:
        return EmbedRenderer(
            syntax_registry=self._syntax_registry,
            rich_text_markdown_converter=self._rich_text_markdown_converter,
        )

    def _create_equation_renderer(self) -> EquationRenderer:
        return EquationRenderer(syntax_registry=self._syntax_registry)

    def _create_table_of_contents_renderer(self) -> TableOfContentsRenderer:
        return TableOfContentsRenderer(syntax_registry=self._syntax_registry)

    def _create_breadcrumb_renderer(self) -> BreadcrumbRenderer:
        return BreadcrumbRenderer(syntax_registry=self._syntax_registry)

    def _create_table_renderer(self) -> TableRenderer:
        return TableRenderer(rich_text_markdown_converter=self._rich_text_markdown_converter)

    def _create_table_row_handler(self) -> TableRowHandler:
        return TableRowHandler()

    def _create_paragraph_renderer(self) -> ParagraphRenderer:
        return ParagraphRenderer(rich_text_markdown_converter=self._rich_text_markdown_converter)

    def _create_fallback_renderer(self) -> FallbackRenderer:
        return FallbackRenderer()
