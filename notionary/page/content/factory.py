from notionary.blocks.client import NotionBlockHttpClient
from notionary.page.content.parser.factory import ConverterChainFactory
from notionary.page.content.parser.post_processing.handlers import RichTextLengthTruncationPostProcessor
from notionary.page.content.parser.post_processing.service import BlockPostProcessor
from notionary.page.content.parser.pre_processsing.handlers import ColumnSyntaxPreProcessor, WhitespacePreProcessor
from notionary.page.content.parser.pre_processsing.service import MarkdownPreProcessor
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.page.content.service import PageContentService


class PageContentServiceFactory:
    def __init__(self, converter_chain_factory: ConverterChainFactory | None = None) -> None:
        self._converter_chain_factory = converter_chain_factory or ConverterChainFactory()

    def create(self, page_id: str, block_client: NotionBlockHttpClient) -> PageContentService:
        markdown_converter = self._create_markdown_converter()
        return PageContentService(
            page_id=page_id,
            block_client=block_client,
            markdown_converter=markdown_converter,
        )

    def _create_markdown_converter(self) -> MarkdownToNotionConverter:
        line_parser = self._converter_chain_factory.create()
        markdown_pre_processor = self._create_markdown_preprocessor()
        block_post_processor = self._create_post_processor()

        return MarkdownToNotionConverter(
            line_parser=line_parser,
            pre_processor=markdown_pre_processor,
            post_processor=block_post_processor,
        )

    def _create_markdown_preprocessor(self) -> MarkdownPreProcessor:
        pre_processor = MarkdownPreProcessor()
        pre_processor.register(ColumnSyntaxPreProcessor())
        pre_processor.register(WhitespacePreProcessor())
        return pre_processor

    def _create_post_processor(self) -> BlockPostProcessor:
        post_processor = BlockPostProcessor()
        post_processor.register(RichTextLengthTruncationPostProcessor())
        return post_processor
