from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import BlockRenderingContext
from notionary.page.content.renderer.post_processing import NumberedListFixer
from notionary.page.content.renderer.renderers import (
    AudioRenderer,
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
from notionary.utils.mixins.logging import LoggingMixin


class NotionToMarkdownConverter(LoggingMixin):
    def __init__(
        self,
        block_registry: BlockRegistry,
        numbered_list_fixer: NumberedListFixer | None = None,
        toggle_handler: ToggleRenderer | None = None,
        toggleable_heading_handler: ToggleableHeadingRenderer | None = None,
        heading_handler: HeadingRenderer | None = None,
        callout_handler: CalloutRenderer | None = None,
        code_handler: CodeRenderer | None = None,
        quote_handler: QuoteRenderer | None = None,
        todo_handler: TodoRenderer | None = None,
        bulleted_list_handler: BulletedListRenderer | None = None,
        divider_handler: DividerRenderer | None = None,
        column_list_handler: ColumnListRenderer | None = None,
        column_handler: ColumnRenderer | None = None,
        numbered_list_handler: NumberedListRenderer | None = None,
        bookmark_handler: BookmarkRenderer | None = None,
        image_handler: ImageRenderer | None = None,
        video_handler: VideoRenderer | None = None,
        audio_handler: AudioRenderer | None = None,
        file_handler: FileRenderer | None = None,
        pdf_handler: PdfRenderer | None = None,
        embed_handler: EmbedRenderer | None = None,
        equation_handler: EquationRenderer | None = None,
        table_of_contents_handler: TableOfContentsRenderer | None = None,
        breadcrumb_handler: BreadcrumbRenderer | None = None,
        table_handler: TableRenderer | None = None,
        table_row_handler: TableRowHandler | None = None,
        paragraph_handler: ParagraphRenderer | None = None,
        fallback_handler: FallbackRenderer | None = None,
    ) -> None:
        self._block_registry = block_registry
        self._numbered_list_fixer = numbered_list_fixer or NumberedListFixer()

        self._toggle_handler = toggle_handler
        self._toggleable_heading_handler = toggleable_heading_handler
        self._heading_handler = heading_handler
        self._callout_handler = callout_handler
        self._code_handler = code_handler
        self._quote_handler = quote_handler
        self._todo_handler = todo_handler
        self._bulleted_list_handler = bulleted_list_handler
        self._divider_handler = divider_handler
        self._column_list_handler = column_list_handler
        self._column_handler = column_handler
        self._numbered_list_handler = numbered_list_handler
        self._bookmark_handler = bookmark_handler
        self._image_handler = image_handler
        self._video_handler = video_handler
        self._audio_handler = audio_handler
        self._file_handler = file_handler
        self._pdf_handler = pdf_handler
        self._embed_handler = embed_handler
        self._equation_handler = equation_handler
        self._table_of_contents_handler = table_of_contents_handler
        self._breadcrumb_handler = breadcrumb_handler
        self._table_handler = table_handler
        self._table_row_handler = table_row_handler
        self._paragraph_handler = paragraph_handler
        self._fallback_handler = fallback_handler

        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        toggle_handler = self._toggle_handler or ToggleRenderer()
        toggleable_heading_handler = self._toggleable_heading_handler or ToggleableHeadingRenderer()
        heading_handler = self._heading_handler or HeadingRenderer()
        callout_handler = self._callout_handler or CalloutRenderer()
        code_handler = self._code_handler or CodeRenderer()
        quote_handler = self._quote_handler or QuoteRenderer()
        todo_handler = self._todo_handler or TodoRenderer()
        bulleted_list_handler = self._bulleted_list_handler or BulletedListRenderer()
        divider_handler = self._divider_handler or DividerRenderer()
        column_list_handler = self._column_list_handler or ColumnListRenderer()
        column_handler = self._column_handler or ColumnRenderer()
        numbered_list_handler = self._numbered_list_handler or NumberedListRenderer()
        bookmark_handler = self._bookmark_handler or BookmarkRenderer()
        image_handler = self._image_handler or ImageRenderer()
        video_handler = self._video_handler or VideoRenderer()
        audio_handler = self._audio_handler or AudioRenderer()
        file_handler = self._file_handler or FileRenderer()
        pdf_handler = self._pdf_handler or PdfRenderer()
        embed_handler = self._embed_handler or EmbedRenderer()
        equation_handler = self._equation_handler or EquationRenderer()
        table_of_contents_handler = self._table_of_contents_handler or TableOfContentsRenderer()
        breadcrumb_handler = self._breadcrumb_handler or BreadcrumbRenderer()
        table_handler = self._table_handler or TableRenderer()
        table_row_handler = self._table_row_handler or TableRowHandler()
        paragraph_handler = self._paragraph_handler or ParagraphRenderer()
        fallback_handler = self._fallback_handler or FallbackRenderer()

        # Chain handlers - most specific first, paragraph as fallback, fallback as final catch-all
        toggle_handler.set_next(toggleable_heading_handler).set_next(heading_handler).set_next(
            callout_handler
        ).set_next(code_handler).set_next(quote_handler).set_next(todo_handler).set_next(
            bulleted_list_handler
        ).set_next(divider_handler).set_next(column_list_handler).set_next(column_handler).set_next(
            numbered_list_handler
        ).set_next(bookmark_handler).set_next(image_handler).set_next(video_handler).set_next(audio_handler).set_next(
            file_handler
        ).set_next(pdf_handler).set_next(embed_handler).set_next(equation_handler).set_next(
            table_of_contents_handler
        ).set_next(breadcrumb_handler).set_next(table_handler).set_next(table_row_handler).set_next(
            paragraph_handler
        ).set_next(fallback_handler)

        self._handler_chain = toggle_handler

    async def convert(self, blocks: list[Block], indent_level: int = 0) -> str:
        if not blocks:
            return ""

        rendered_block_parts = []
        current_block_index = 0

        while current_block_index < len(blocks):
            context = self._create_rendering_context(blocks, current_block_index, indent_level)
            await self._handler_chain.handle(context)

            if context.markdown_result:
                rendered_block_parts.append(context.markdown_result)

            current_block_index += 1

        result = self._join_rendered_blocks(rendered_block_parts, indent_level)

        result = self._numbered_list_fixer.process(result)

        return result

    def _create_rendering_context(
        self, blocks: list[Block], block_index: int, indent_level: int
    ) -> BlockRenderingContext:
        block = blocks[block_index]
        return BlockRenderingContext(
            block=block,
            indent_level=indent_level,
            convert_children_callback=self.convert,
        )

    def _join_rendered_blocks(self, rendered_parts: list[str], indent_level: int) -> str:
        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(rendered_parts)
