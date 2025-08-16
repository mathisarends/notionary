from notionary.blocks.block_client import NotionBlockClient
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.reader.block_processor import BlockProcessor
from notionary.util import LoggingMixin


class PageContentRetriever(LoggingMixin):
    """Retrieves Notion page content and converts it to Markdown using chain of responsibility."""

    def __init__(
        self,
        page_id: str,
        block_registry: BlockRegistry,
    ):
        self.page_id = page_id
        self._block_registry = block_registry
        self.client = NotionBlockClient()
        self._block_processor = BlockProcessor(block_registry)

    async def get_page_content(self) -> str:
        """
        Retrieve page content and convert it to Markdown.
        Uses the chain of responsibility pattern for scalable block processing.
        """
        blocks = await self.client.get_blocks_by_page_id_recursively(
            page_id=self.page_id
        )

        return self._block_processor.convert_blocks_to_markdown(blocks, indent_level=0)