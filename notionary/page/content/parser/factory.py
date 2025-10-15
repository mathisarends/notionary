from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.page.content.parser.parsers import (
    AudioParser,
    BookmarkParser,
    BreadcrumbParser,
    BulletedListParser,
    CalloutParser,
    CaptionParser,
    CodeParser,
    ColumnListParser,
    ColumnParser,
    DividerParser,
    EmbedParser,
    EquationParser,
    FileParser,
    HeadingParser,
    ImageParser,
    LineParser,
    NumberedListParser,
    ParagraphParser,
    PdfParser,
    QuoteParser,
    SpaceParser,
    TableOfContentsParser,
    TableParser,
    TodoParser,
    ToggleParser,
    VideoParser,
)
from notionary.page.content.syntax.service import SyntaxRegistry


class ConverterChainFactory:
    def __init__(
        self,
        rich_text_converter: MarkdownRichTextConverter | None = None,
        syntax_registry: SyntaxRegistry | None = None,
    ) -> None:
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()
        self._syntax_registry = syntax_registry or SyntaxRegistry()

    def create(self) -> LineParser:
        # multi-line (structural) blocks
        code_parser = self._create_code_parser()
        equation_parser = self._create_equation_parser()
        table_parser = self._create_table_parser()
        column_parser = self._create_column_parser()
        column_list_parser = self._create_column_list_parser()
        toggle_parser = self._create_toggle_parser()

        # Single-line blocks
        divider_parser = self._create_divider_parser()
        breadcrumb_parser = self._create_breadcrumb_parser()
        table_of_contents_parser = self._create_table_of_contents_parser()
        space_parser = self._create_space_parser()
        heading_parser = self._create_heading_parser()
        quote_parser = self._create_quote_parser()
        callout_parser = self._create_callout_parser()
        todo_parser = self._create_todo_parser()
        bulleted_list_parser = self._create_bulleted_list_parser()
        numbered_list_parser = self._create_numbered_list_parser()

        # Media blocks
        bookmark_parser = self._create_bookmark_parser()
        embed_parser = self._create_embed_parser()
        image_parser = self._create_image_parser()
        video_parser = self._create_video_parser()
        audio_parser = self._create_audio_parser()
        file_parser = self._create_file_parser()
        pdf_parser = self._create_pdf_parser()

        # Caption and Fallback
        caption_parser = self._create_caption_parser()
        paragraph_parser = self._create_paragraph_parser()

        (
            code_parser.set_next(equation_parser)
            .set_next(table_parser)
            .set_next(column_parser)
            .set_next(column_list_parser)
            .set_next(toggle_parser)
            .set_next(divider_parser)
            .set_next(breadcrumb_parser)
            .set_next(table_of_contents_parser)
            .set_next(space_parser)
            .set_next(heading_parser)
            .set_next(quote_parser)
            .set_next(callout_parser)
            .set_next(todo_parser)
            .set_next(bulleted_list_parser)
            .set_next(numbered_list_parser)
            .set_next(bookmark_parser)
            .set_next(embed_parser)
            .set_next(image_parser)
            .set_next(video_parser)
            .set_next(audio_parser)
            .set_next(file_parser)
            .set_next(pdf_parser)
            .set_next(caption_parser)
            .set_next(paragraph_parser)
        )

        return code_parser

    def _create_code_parser(self) -> CodeParser:
        return CodeParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_equation_parser(self) -> EquationParser:
        return EquationParser(syntax_registry=self._syntax_registry)

    def _create_table_parser(self) -> TableParser:
        return TableParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_column_parser(self) -> ColumnParser:
        return ColumnParser(syntax_registry=self._syntax_registry)

    def _create_column_list_parser(self) -> ColumnListParser:
        return ColumnListParser(syntax_registry=self._syntax_registry)

    def _create_toggle_parser(self) -> ToggleParser:
        return ToggleParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_divider_parser(self) -> DividerParser:
        return DividerParser(syntax_registry=self._syntax_registry)

    def _create_breadcrumb_parser(self) -> BreadcrumbParser:
        return BreadcrumbParser(syntax_registry=self._syntax_registry)

    def _create_table_of_contents_parser(self) -> TableOfContentsParser:
        return TableOfContentsParser(syntax_registry=self._syntax_registry)

    def _create_space_parser(self) -> SpaceParser:
        return SpaceParser(syntax_registry=self._syntax_registry)

    def _create_heading_parser(self) -> HeadingParser:
        return HeadingParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_quote_parser(self) -> QuoteParser:
        return QuoteParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_callout_parser(self) -> CalloutParser:
        return CalloutParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_todo_parser(self) -> TodoParser:
        return TodoParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_bulleted_list_parser(self) -> BulletedListParser:
        return BulletedListParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_numbered_list_parser(self) -> NumberedListParser:
        return NumberedListParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_bookmark_parser(self) -> BookmarkParser:
        return BookmarkParser(syntax_registry=self._syntax_registry)

    def _create_embed_parser(self) -> EmbedParser:
        return EmbedParser(syntax_registry=self._syntax_registry)

    def _create_image_parser(self) -> ImageParser:
        return ImageParser(syntax_registry=self._syntax_registry)

    def _create_video_parser(self) -> VideoParser:
        return VideoParser(syntax_registry=self._syntax_registry)

    def _create_audio_parser(self) -> AudioParser:
        return AudioParser(syntax_registry=self._syntax_registry)

    def _create_file_parser(self) -> FileParser:
        return FileParser(syntax_registry=self._syntax_registry)

    def _create_pdf_parser(self) -> PdfParser:
        return PdfParser(syntax_registry=self._syntax_registry)

    def _create_caption_parser(self) -> CaptionParser:
        return CaptionParser(
            syntax_registry=self._syntax_registry,
            rich_text_converter=self._rich_text_converter,
        )

    def _create_paragraph_parser(self) -> ParagraphParser:
        return ParagraphParser(rich_text_converter=self._rich_text_converter)
