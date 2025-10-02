from notionary.blocks.block_http_client import NotionBlockHttpClient
from notionary.blocks.models import Block
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.utils.mixins.logging import LoggingMixin


# TODO: Refactor those files here
class PageContentDeletingService(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry) -> None:
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockHttpClient()

    async def clear_page_content(self) -> None:
        children_response = await self._block_client.get_block_children(block_id=self.page_id)

        if not children_response or not children_response.results:
            return None

        success = True
        for block in children_response.results:
            block_success = await self._delete_block_with_children(block)
            if not block_success:
                success = False

        if not success:
            self.logger.warning("Some blocks could not be deleted")

    async def _delete_block_with_children(self, block: Block) -> None:
        if block.has_children:
            return

        await self._delete_block_children(block)

        return await self._delete_single_block(block)

    async def _delete_block_children(self, block: Block) -> bool:
        try:
            children_blocks = await self._block_client.get_all_block_children(block.id)

            if not children_blocks:
                self.logger.debug("No children found for block: %s", block.id)
                return True

            self.logger.debug(
                "Found %d children to delete for block: %s",
                len(children_blocks),
                block.id,
            )

            # Delete all children recursively
            for child_block in children_blocks:
                if not await self._delete_block_with_children(child_block):
                    self.logger.error("Failed to delete child block: %s", child_block.id)
                    return False

            self.logger.debug("Successfully deleted all children of block: %s", block.id)
            return True

        except Exception as e:
            self.logger.error("Failed to delete children of block %s: %s", block.id, str(e))
            return False

    async def _delete_single_block(self, block: Block) -> bool:
        deleted_block: Block | None = await self._block_client.delete_block(block.id)

        if deleted_block is None:
            self.logger.error("Failed to delete block: %s", block.id)
            return False

        if deleted_block.archived or deleted_block.in_trash:
            self.logger.debug("Successfully deleted/archived block: %s", block.id)
            return True
        else:
            self.logger.warning("Block %s was not properly archived/deleted", block.id)
            return False
