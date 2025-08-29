"""
Dedicated processor for converting MarkdownDocumentModel to MarkdownBuilder.
Handles the mapping from structured Pydantic models to MarkdownBuilder instances.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.markdown.markdown_builder import MarkdownBuilder

from notionary.markdown.markdown_document_model import (
    MarkdownBlock,
    MarkdownDocumentModel,
)

from notionary.blocks.bookmark.bookmark_markdown_node import BookmarkMarkdownNode
from notionary.blocks.breadcrumbs.breadcrumb_markdown_node import BreadcrumbMarkdownNode
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import BulletedListMarkdownNode
from notionary.blocks.callout.callout_markdown_node import CalloutMarkdownNode
from notionary.blocks.code.code_markdown_node import CodeMarkdownNode
from notionary.blocks.column.column_list_markdown_node import ColumnListMarkdownNode
from notionary.blocks.column.column_markdown_node import ColumnMarkdownNode
from notionary.blocks.divider.divider_markdown_node import DividerMarkdownNode
from notionary.blocks.embed.embed_markdown_node import EmbedMarkdownNode
from notionary.blocks.equation.equation_element_markdown_node import EquationMarkdownNode
from notionary.blocks.file.file_element_markdown_node import FileMarkdownNode
from notionary.blocks.heading.heading_markdown_node import HeadingMarkdownNode
from notionary.blocks.image_block.image_markdown_node import ImageMarkdownNode
from notionary.blocks.numbered_list.numbered_list_markdown_node import NumberedListMarkdownNode
from notionary.blocks.paragraph.paragraph_markdown_node import ParagraphMarkdownNode
from notionary.blocks.pdf.pdf_markdown_node import PdfMarkdownNode
from notionary.blocks.quote.quote_markdown_node import QuoteMarkdownNode
from notionary.blocks.table.table_markdown_node import TableMarkdownNode
from notionary.blocks.table_of_contents.table_of_contents_markdown_node import TableOfContentsMarkdownNode
from notionary.blocks.todo.todo_markdown_node import TodoMarkdownNode
from notionary.blocks.toggle.toggle_markdown_node import ToggleMarkdownNode
from notionary.blocks.toggleable_heading.toggleable_heading_markdown_node import ToggleableHeadingMarkdownNode
from notionary.blocks.video.video_markdown_node import VideoMarkdownNode
from notionary.blocks.audio.audio_markdown_node import AudioMarkdownNode
from notionary.markdown.block_params import (
    AudioBlockParams,
    BookmarkBlockParams,
    BreadcrumbBlockParams,
    BulletedListBlockParams,
    CalloutBlockParams,
    CodeBlockParams,
    ColumnBlockParams,
    DividerBlockParams,
    EmbedBlockParams,
    EquationBlockParams,
    FileBlockParams,
    HeadingBlockParams,
    ImageBlockParams,
    NumberedListBlockParams,
    ParagraphBlockParams,
    PdfBlockParams,
    QuoteBlockParams,
    TableBlockParams,
    TableOfContentsBlockParams,
    TodoBlockParams,
    ToggleBlockParams,
    ToggleableHeadingBlockParams,
    VideoBlockParams,
)


class MarkdownModelProcessor:
    """
    Processes MarkdownDocumentModel instances and converts them to MarkdownBuilder.

    Handles the mapping from structured Pydantic models to MarkdownBuilder instances,
    separating this responsibility from the fluent builder API.
    """

    def __init__(self, builder: MarkdownBuilder):
        """
        Initialize processor with a MarkdownBuilder instance.

        Args:
            builder: The MarkdownBuilder to populate with nodes
        """
        self.builder = builder
        self._setup_block_processors()

    def process(self, input: MarkdownDocumentModel | list[MarkdownBlock]) -> None:
        """
        Process a MarkdownDocumentModel or a list of MarkdownBlock instances and populate the builder.

        Args:
            input: The MarkdownDocumentModel or list of MarkdownBlock instances to process
        """
        if isinstance(input, MarkdownDocumentModel):
            blocks = input.blocks
        else:
            blocks = input

        for block in blocks:
            processor = self._block_processors.get(block.type)
            if processor:
                processor(block)  # Pass the block directly, not block.params
            else:
                # More explicit error handling
                available_types = ", ".join(sorted(self._block_processors.keys()))
                raise ValueError(
                    f"Unsupported block type '{block.type}'. "
                    f"Available types: {available_types}"
                )

    # Block processor methods
    def _add_heading(self, block: HeadingBlockParams) -> None:
        """Add a heading block."""
        self.builder.children.append(HeadingMarkdownNode(text=block.text, level=block.level))

    def _add_paragraph(self, block: ParagraphBlockParams) -> None:
        """Add a paragraph block."""
        self.builder.children.append(ParagraphMarkdownNode(text=block.text))

    def _add_quote(self, block: QuoteBlockParams) -> None:
        """Add a quote block."""
        self.builder.children.append(QuoteMarkdownNode(text=block.text))

    def _add_bulleted_list(self, block: BulletedListBlockParams) -> None:
        """Add a bulleted list block."""
        self.builder.children.append(BulletedListMarkdownNode(texts=block.texts))

    def _add_numbered_list(self, block: NumberedListBlockParams) -> None:
        """Add a numbered list block."""
        self.builder.children.append(NumberedListMarkdownNode(texts=block.texts))

    def _add_todo(self, block: TodoBlockParams) -> None:
        """Add a todo block."""
        self.builder.children.append(TodoMarkdownNode(text=block.text, checked=block.checked))

    def _add_callout(self, block: CalloutBlockParams) -> None:
        """Add a callout block."""
        self.builder.children.append(CalloutMarkdownNode(text=block.text, emoji=block.emoji))

    def _add_code(self, block: CodeBlockParams) -> None:
        """Add a code block."""
        self.builder.children.append(CodeMarkdownNode(code=block.code, language=block.language, caption=block.caption))

    def _add_image(self, block: ImageBlockParams) -> None:
        """Add an image block."""
        self.builder.children.append(ImageMarkdownNode(url=block.url, caption=block.caption, alt=block.alt))

    def _add_video(self, block: VideoBlockParams) -> None:
        """Add a video block."""
        self.builder.children.append(VideoMarkdownNode(url=block.url, caption=block.caption))

    def _add_audio(self, block: AudioBlockParams) -> None:
        """Add an audio block."""
        self.builder.children.append(AudioMarkdownNode(url=block.url, caption=block.caption))

    def _add_file(self, block: FileBlockParams) -> None:
        """Add a file block."""
        self.builder.children.append(FileMarkdownNode(url=block.url, caption=block.caption))

    def _add_pdf(self, block: PdfBlockParams) -> None:
        """Add a PDF block."""
        self.builder.children.append(PdfMarkdownNode(url=block.url, caption=block.caption))

    def _add_bookmark(self, block: BookmarkBlockParams) -> None:
        """Add a bookmark block."""
        self.builder.children.append(BookmarkMarkdownNode(url=block.url, title=block.title, caption=block.caption))

    def _add_embed(self, block: EmbedBlockParams) -> None:
        """Add an embed block."""
        self.builder.children.append(EmbedMarkdownNode(url=block.url, caption=block.caption))

    def _add_table(self, block: TableBlockParams) -> None:
        """Add a table block."""
        self.builder.children.append(TableMarkdownNode(headers=block.headers, rows=block.rows))

    def _add_divider(self, block: DividerBlockParams) -> None:
        """Add a divider block."""
        self.builder.children.append(DividerMarkdownNode())

    def _add_equation(self, block: EquationBlockParams) -> None:
        """Add an equation block."""
        self.builder.children.append(EquationMarkdownNode(expression=block.expression))

    def _add_table_of_contents(self, block: TableOfContentsBlockParams) -> None:
        """Add a table of contents block."""
        self.builder.children.append(TableOfContentsMarkdownNode(color=block.color))

    def _add_toggle(self, block: ToggleBlockParams) -> None:
        """Add a toggle block."""
        from notionary.markdown.markdown_builder import MarkdownBuilder

        child_builder = MarkdownBuilder()
        child_processor = MarkdownModelProcessor(child_builder)
        child_processor.process(block.children)

        self.builder.children.append(
            ToggleMarkdownNode(title=block.title, children=child_builder.children)
        )

    def _add_toggleable_heading(self, block: ToggleableHeadingBlockParams) -> None:
        """Add a toggleable heading block."""
        from notionary.markdown.markdown_builder import MarkdownBuilder

        # Create nested builder for children
        child_builder = MarkdownBuilder()
        child_processor = MarkdownModelProcessor(child_builder)
        child_processor.process(block.children)

        self.builder.children.append(
            ToggleableHeadingMarkdownNode(
                text=block.text, level=block.level, children=child_builder.children
            )
        )

    def _add_columns(self, block: ColumnBlockParams) -> None:
        """Add a columns block."""
        from notionary.markdown.markdown_builder import MarkdownBuilder

        column_nodes = []

        for i, column_blocks in enumerate(block.columns):
            width_ratio = (
                block.width_ratios[i]
                if block.width_ratios and i < len(block.width_ratios)
                else None
            )

            col_builder = MarkdownBuilder()
            col_processor = MarkdownModelProcessor(col_builder)
            col_processor.process(column_blocks)

            column_node = ColumnMarkdownNode(
                children=col_builder.children,
                width_ratio=width_ratio 
            )
            column_nodes.append(column_node)

        # Create ColumnListMarkdownNode with properly typed columns
        self.builder.children.append(ColumnListMarkdownNode(columns=column_nodes))

    def _add_breadcrumb(self, block: BreadcrumbBlockParams) -> None:
        """Add a breadcrumb block."""
        self.builder.children.append(BreadcrumbMarkdownNode())

    def _add_space(self, block) -> None:
        """Add a space block."""
        self.builder.children.append(ParagraphMarkdownNode(text=""))

    def _setup_block_processors(self) -> None:
        """Setup mapping of block types to their processor methods."""
        self._block_processors = {
            "heading": self._add_heading,
            "paragraph": self._add_paragraph,
            "quote": self._add_quote,
            "bulleted_list": self._add_bulleted_list,
            "numbered_list": self._add_numbered_list,
            "todo": self._add_todo,
            "callout": self._add_callout,
            "code": self._add_code,
            "image": self._add_image,
            "video": self._add_video,
            "audio": self._add_audio,
            "file": self._add_file,
            "pdf": self._add_pdf,
            "bookmark": self._add_bookmark,
            "embed": self._add_embed,
            "table": self._add_table,
            "divider": self._add_divider,
            "equation": self._add_equation,
            "table_of_contents": self._add_table_of_contents,
            "toggle": self._add_toggle,
            "toggleable_heading": self._add_toggleable_heading,
            "columns": self._add_columns,
            "breadcrumb": self._add_breadcrumb,
            "space": self._add_space,
        }
