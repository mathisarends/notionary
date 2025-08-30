from typing import Optional

from notionary.blocks.client import NotionBlockClient
from notionary.blocks.models import Block
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.util import LoggingMixin


class PageContentDeletingService(LoggingMixin):
    """Service responsible for deleting page content and blocks."""

    def __init__(self, page_id: str, block_registry: BlockRegistry):
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockClient()
        self._content_retriever = PageContentRetriever(block_registry=block_registry)

    async def clear_page_content(self) -> Optional[str]:
        """Clear all content of the page and return deleted content as markdown."""
        try:
            children_response = await self._block_client.get_block_children(
                block_id=self.page_id
            )

            if not children_response or not children_response.results:
                return None

            # Use PageContentRetriever for sophisticated markdown conversion
            deleted_content = await self._content_retriever._convert_blocks_to_markdown(
                children_response.results, indent_level=0
            )

            # Delete blocks
            success = True
            for block in children_response.results:
                block_success = await self._delete_block_with_children(block)
                if not block_success:
                    success = False

            if not success:
                self.logger.warning("Some blocks could not be deleted")

            return deleted_content if deleted_content else None

        except Exception:
            self.logger.error("Error clearing page content", exc_info=True)
            return None

    async def _delete_block_with_children(self, block: Block) -> bool:
        """Delete a block and all its children recursively."""
        if not block.id:
            self.logger.error("Block has no valid ID")
            return False

        self.logger.debug("Deleting block: %s (type: %s)", block.id, block.type)

        try:
            if block.has_children and not await self._delete_block_children(block):
                return False

            return await self._delete_single_block(block)

        except Exception as e:
            self.logger.error("Failed to delete block %s: %s", block.id, str(e))
            return False

    async def _delete_block_children(self, block: Block) -> bool:
        """Delete all children of a block."""
        self.logger.debug("Block %s has children, deleting children first", block.id)

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
                    self.logger.error(
                        "Failed to delete child block: %s", child_block.id
                    )
                    return False

            self.logger.debug(
                "Successfully deleted all children of block: %s", block.id
            )
            return True

        except Exception as e:
            self.logger.error(
                "Failed to delete children of block %s: %s", block.id, str(e)
            )
            return False

    async def _delete_single_block(self, block: Block) -> bool:
        """Delete a single block."""
        deleted_block: Optional[Block] = await self._block_client.delete_block(block.id)

        if deleted_block is None:
            self.logger.error("Failed to delete block: %s", block.id)
            return False

        if deleted_block.archived or deleted_block.in_trash:
            self.logger.debug("Successfully deleted/archived block: %s", block.id)
            return True
        else:
            self.logger.warning("Block %s was not properly archived/deleted", block.id)
            return False
