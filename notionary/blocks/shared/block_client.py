from typing import Optional, Dict, Any
from notionary.base_notion_client import BaseNotionClient
from notionary.util import singleton
from notionary.blocks.shared.models import Block, BlockChildrenResponse


@singleton
class NotionBlockClient(BaseNotionClient):
    """
    Client for Notion Block API operations.
    """

    async def get_block(self, block_id: str) -> Optional[Block]:
        """
        Retrieves a single block by its ID.
        """
        self.logger.debug("Retrieving block: %s", block_id)

        response = await self.get(f"blocks/{block_id}")
        if response:
            try:
                return Block.model_validate(response)
            except Exception as e:
                self.logger.error("Failed to parse block response: %s", str(e))
                return None
        return None

    async def get_block_children(
        self, block_id: str, start_cursor: Optional[str] = None, page_size: int = 100
    ) -> Optional[BlockChildrenResponse]:
        """
        Retrieves the children of a block with pagination support.
        """
        self.logger.debug("Retrieving children of block: %s", block_id)

        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get(f"blocks/{block_id}/children", params=params)
        if response:
            try:
                return BlockChildrenResponse.model_validate(response)
            except Exception as e:
                self.logger.error("Failed to parse block children response: %s", str(e))
                return None
        return None

    async def get_all_block_children(self, block_id: str) -> list[Block]:
        """
        Retrieves ALL children of a block, handling pagination automatically.
        """
        all_blocks = []
        cursor = None

        while True:
            response = await self.get_block_children(
                block_id=block_id, start_cursor=cursor, page_size=100
            )

            if not response:
                break

            all_blocks.extend(response.results)

            if not response.has_more:
                break

            cursor = response.next_cursor

        self.logger.debug(
            "Retrieved %d total children for block %s", len(all_blocks), block_id
        )
        return all_blocks

    async def wappend_block_children(
        self, block_id: str, children: list[Dict[str, Any]], after: Optional[str] = None
    ) -> Optional[BlockChildrenResponse]:
        """
        Appends new child blocks to a parent block.
        Automatically handles batching for more than 100 blocks.
        """
        if not children:
            self.logger.warning("No children provided to append")
            return None

        self.logger.debug("Appending %d children to block: %s", len(children), block_id)

        # If 100 or fewer blocks, use single request
        if len(children) <= 100:
            return await self._append_single_batch(block_id, children, after)

        # For more than 100 blocks, use batch processing
        return await self._append_multiple_batches(block_id, children, after)

    async def _append_single_batch(
        self, block_id: str, children: list[Dict[str, Any]], after: Optional[str] = None
    ) -> Optional[BlockChildrenResponse]:
        """
        Appends a single batch of blocks (≤100).
        """
        data = {"children": children}
        if after:
            data["after"] = after

        response = await self.patch(f"blocks/{block_id}/children", data)
        if response:
            try:
                return BlockChildrenResponse.model_validate(response)
            except Exception as e:
                self.logger.error("Failed to parse append response: %s", str(e))
                return None
        return None

    async def _append_multiple_batches(
        self, block_id: str, children: list[Dict[str, Any]], after: Optional[str] = None
    ) -> Optional[BlockChildrenResponse]:
        """
        Appends multiple batches of blocks, handling pagination.
        """
        all_results = []
        current_after = after
        batch_size = 100

        self.logger.info(
            "Processing %d blocks in batches of %d", len(children), batch_size
        )

        # Process blocks in chunks of 100
        for i in range(0, len(children), batch_size):
            batch = children[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(children) + batch_size - 1) // batch_size

            self.logger.debug(
                "Processing batch %d/%d (%d blocks)",
                batch_num,
                total_batches,
                len(batch),
            )

            # Append current batch
            response = await self._append_single_batch(block_id, batch, current_after)

            if not response:
                self.logger.error(
                    "Failed to append batch %d/%d", batch_num, total_batches
                )
                # Return partial results if we have any
                if all_results:
                    return self._combine_batch_responses(all_results)
                return None

            all_results.append(response)

            # Update 'after' to the last block ID from this batch for next iteration
            if response.results:
                current_after = response.results[-1].id

            self.logger.debug(
                "Successfully appended batch %d/%d", batch_num, total_batches
            )

        self.logger.info(
            "Successfully appended all %d blocks in %d batches",
            len(children),
            len(all_results),
        )

        # Combine all batch responses into a single response
        return self._combine_batch_responses(all_results)

    def _combine_batch_responses(
        self, responses: list[BlockChildrenResponse]
    ) -> BlockChildrenResponse:
        """
        Combines multiple batch responses into a single response.
        """
        if not responses:
            # Return empty response structure
            return BlockChildrenResponse(
                object="list",
                results=[],
                next_cursor=None,
                has_more=False,
                type="block",
                block={},
                request_id="",
            )

        # Use the first response as template and combine all results
        combined = responses[0]
        all_blocks = []

        for response in responses:
            all_blocks.extend(response.results)

        # Create new combined response
        return BlockChildrenResponse(
            object=combined.object,
            results=all_blocks,
            next_cursor=None,  # No pagination in combined result
            has_more=False,  # All blocks are included
            type=combined.type,
            block=combined.block,
            request_id=responses[-1].request_id,  # Use last request ID
        )

    async def update_block(
        self, block_id: str, block_data: Dict[str, Any], archived: Optional[bool] = None
    ) -> Optional[Block]:
        """
        Updates an existing block.
        """
        self.logger.debug("Updating block: %s", block_id)

        data = block_data.copy()
        if archived is not None:
            data["archived"] = archived

        response = await self.patch(f"blocks/{block_id}", data)
        if response:
            try:
                return Block.model_validate(response)
            except Exception as e:
                self.logger.error("Failed to parse update response: %s", str(e))
                return None
        return None

    async def delete_block(self, block_id: str) -> Optional[Block]:
        """
        Deletes (archives) a block.
        """
        self.logger.debug("Deleting block: %s", block_id)

        success = await self.delete(f"blocks/{block_id}")
        if success:
            # After deletion, retrieve the block to return the updated state
            return await self.get_block(block_id)
        return None

    async def archive_block(self, block_id: str) -> Optional[Block]:
        """
        Archives a block by setting archived=True.
        """
        self.logger.debug("Archiving block: %s", block_id)

        return await self.update_block(block_id=block_id, block_data={}, archived=True)

    async def unarchive_block(self, block_id: str) -> Optional[Block]:
        """
        Unarchives a block by setting archived=False.
        """
        self.logger.debug("Unarchiving block: %s", block_id)

        return await self.update_block(block_id=block_id, block_data={}, archived=False)
