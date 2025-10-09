import asyncio

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.schemas import Block
from notionary.utils.async_retry import async_retry
from notionary.utils.mixins.logging import LoggingMixin


class PageContentDeletingService(LoggingMixin):
    def __init__(self, page_id: str, block_client: NotionBlockHttpClient) -> None:
        self.page_id = page_id
        self._block_client = block_client

    async def clear_page_content(self) -> None:
        children_response = await self._block_client.get_block_children(block_id=self.page_id)

        if not children_response or not children_response.results:
            return

        await asyncio.gather(*[self._delete_single_block(block) for block in children_response.results])

    @async_retry(max_retries=5, initial_delay=0.2, backoff_factor=2.0)
    async def _delete_single_block(self, block: Block) -> None:
        await self._block_client.delete_block(block.id)
