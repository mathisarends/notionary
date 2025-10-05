from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.parsers import (
    AudioParser,
    BlockParsingContext,
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
    NumberedListParser,
    ParagraphParser,
    ParentBlockContext,
    PdfParser,
    QuoteParser,
    SpaceParser,
    TableOfContentsParser,
    TableParser,
    TodoParser,
    ToggleableHeadingParser,
    ToggleParser,
    VideoParser,
)
from notionary.page.content.parser.pre_processsing.text_length import (
    NotionTextLengthProcessor,
)
from notionary.utils.mixins.logging import LoggingMixin


class MarkdownToNotionConverter(LoggingMixin):
    def __init__(
        self,
        rich_text_converter: MarkdownRichTextConverter | None = None,
    ) -> None:
        self._text_length_post_processor = NotionTextLengthProcessor()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        code_parser = CodeParser()
        equation_parser = EquationParser()
        table_parser = TableParser()
        column_parser = ColumnParser()
        column_list_parser = ColumnListParser()
        toggleable_heading_parser = ToggleableHeadingParser(self._rich_text_converter)
        toggle_parser = ToggleParser(self._rich_text_converter)

        # Dedicated parsers without mapper dependencies
        divider_parser = DividerParser()
        breadcrumb_parser = BreadcrumbParser()
        table_of_contents_parser = TableOfContentsParser()
        heading_parser = HeadingParser(self._rich_text_converter)
        quote_parser = QuoteParser(self._rich_text_converter)
        callout_parser = CalloutParser(self._rich_text_converter)
        space_parser = SpaceParser()
        todo_parser = TodoParser(self._rich_text_converter)
        bulleted_list_parser = BulletedListParser(self._rich_text_converter)
        numbered_list_parser = NumberedListParser(self._rich_text_converter)
        bookmark_parser = BookmarkParser()
        embed_parser = EmbedParser()
        image_parser = ImageParser()
        video_parser = VideoParser()
        audio_parser = AudioParser()
        file_parser = FileParser()
        pdf_parser = PdfParser()
        caption_parser = CaptionParser(self._rich_text_converter)
        paragraph_parser = ParagraphParser(self._rich_text_converter)

        # Build the chain - order matters!
        # 1. Multi-line blocks first
        code_parser.set_next(equation_parser).set_next(table_parser).set_next(column_parser).set_next(
            column_list_parser
        ).set_next(toggleable_heading_parser).set_next(toggle_parser).set_next(
            # 2. Single-line blocks with specific patterns
            divider_parser
        ).set_next(breadcrumb_parser).set_next(table_of_contents_parser).set_next(space_parser).set_next(
            heading_parser
        ).set_next(quote_parser).set_next(callout_parser).set_next(todo_parser).set_next(bulleted_list_parser).set_next(
            numbered_list_parser
        ).set_next(bookmark_parser).set_next(embed_parser).set_next(image_parser).set_next(video_parser).set_next(
            audio_parser
        ).set_next(file_parser).set_next(pdf_parser).set_next(
            # 3. Caption parser - handles [caption] lines for previous blocks
            caption_parser
        ).set_next(
            # 4. Paragraph as fallback (must be last)
            paragraph_parser
        )

        self._handler_chain = code_parser

    async def convert(self, markdown_text: str) -> list[BlockCreatePayload]:
        if not markdown_text.strip():
            return []

        all_blocks = await self.process_lines(markdown_text)

        all_blocks = self._text_length_post_processor.process(all_blocks)

        return all_blocks

    async def process_lines(self, text: str) -> list[BlockCreatePayload]:
        lines = text.split("\n")
        result_blocks: list[BlockCreatePayload] = []
        parent_stack: list[ParentBlockContext] = []

        current_line_index = 0
        while current_line_index < len(lines):
            line = lines[current_line_index]

            context = self._create_line_processing_context(
                line=line,
                lines=lines,
                line_index=current_line_index,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
            )

            await self._handler_chain.handle(context)

            current_line_index += 1 + context.lines_consumed

        return result_blocks

    def _create_line_processing_context(
        self,
        line: str,
        lines: list[str],
        line_index: int,
        result_blocks: list[BlockCreatePayload],
        parent_stack: list[ParentBlockContext],
    ) -> BlockParsingContext:
        return BlockParsingContext(
            line=line,
            result_blocks=result_blocks,
            parent_stack=parent_stack,
            parse_children_callback=self.process_lines,
            all_lines=lines,
            current_line_index=line_index,
            lines_consumed=0,
        )
