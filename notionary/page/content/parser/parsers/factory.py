from notionary.file_upload.service import NotionFileUpload
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
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)


def create_line_parser() -> LineParser:
    file_upload_service = NotionFileUpload()
    rich_text_converter = create_markdown_to_rich_text_converter()
    syntax_registry = SyntaxDefinitionRegistry()

    code_parser = CodeParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    equation_parser = EquationParser(syntax_registry=syntax_registry)
    table_parser = TableParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    column_parser = ColumnParser(syntax_registry=syntax_registry)
    column_list_parser = ColumnListParser(syntax_registry=syntax_registry)
    toggle_parser = ToggleParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )

    divider_parser = DividerParser(syntax_registry=syntax_registry)
    breadcrumb_parser = BreadcrumbParser(syntax_registry=syntax_registry)
    table_of_contents_parser = TableOfContentsParser(syntax_registry=syntax_registry)
    space_parser = SpaceParser(syntax_registry=syntax_registry)
    heading_parser = HeadingParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    quote_parser = QuoteParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    callout_parser = CalloutParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    todo_parser = TodoParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    bulleted_list_parser = BulletedListParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    numbered_list_parser = NumberedListParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )

    bookmark_parser = BookmarkParser(syntax_registry=syntax_registry)
    embed_parser = EmbedParser(syntax_registry=syntax_registry)
    image_parser = ImageParser(
        syntax_registry=syntax_registry,
        file_upload_service=file_upload_service,
    )
    video_parser = VideoParser(
        syntax_registry=syntax_registry,
        file_upload_service=file_upload_service,
    )
    audio_parser = AudioParser(
        syntax_registry=syntax_registry,
        file_upload_service=file_upload_service,
    )
    file_parser = FileParser(
        syntax_registry=syntax_registry,
        file_upload_service=file_upload_service,
    )
    pdf_parser = PdfParser(
        syntax_registry=syntax_registry,
        file_upload_service=file_upload_service,
    )

    caption_parser = CaptionParser(
        syntax_registry=syntax_registry,
        rich_text_converter=rich_text_converter,
    )
    paragraph_parser = ParagraphParser(rich_text_converter=rich_text_converter)

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
