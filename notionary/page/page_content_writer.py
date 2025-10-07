from collections.abc import Callable

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.markdown.builder import MarkdownBuilder
from notionary.page.content.parser.factory import ConverterChainFactory
from notionary.page.content.parser.pre_processsing.whitespace import process_markdown_whitespace
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.utils.mixins.logging import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        block_client: NotionBlockHttpClient,
        converter_chain_factory: ConverterChainFactory | None = None,
    ) -> None:
        self.page_id = page_id
        self._block_client = block_client
        self._converter_chain_factory = converter_chain_factory or ConverterChainFactory()

        self._markdown_to_notion_converter = self._create_markdown_notion_converter()

    def _create_markdown_notion_converter(self) -> MarkdownToNotionConverter:
        line_parser = self._converter_chain_factory.create()

        return MarkdownToNotionConverter(
            line_parser=line_parser,
            whitespace_processor=process_markdown_whitespace,
        )

    async def append_markdown(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder]),
    ) -> None:
        markdown = self._extract_markdown_from_param(content)

        if not markdown:
            return

        blocks = await self._markdown_to_notion_converter.convert(markdown)

        await self._block_client.append_block_children(block_id=self.page_id, children=blocks)

    def _extract_markdown_from_param(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder]),
    ) -> str:
        if isinstance(content, str):
            return content

        if callable(content):
            builder = MarkdownBuilder()
            content(builder)
            return builder.build()

        raise ValueError(
            "content must be either a string, a NotionContentSchema, a MarkdownDocumentModel, or a callable that takes a MarkdownBuilder"
        )
