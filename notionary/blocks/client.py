from typing import Any

from notionary.blocks.schemas import Block, BlockChildrenResponse, BlockCreatePayload
from notionary.http.client import NotionHttpClient
from notionary.utils.pagination import paginate_notion_api


class NotionBlockHttpClient(NotionHttpClient):
    BATCH_SIZE = 100

    async def get_block(self, block_id: str) -> Block:
        response = await self.get(f"blocks/{block_id}")
        return Block.model_validate(response)

    async def delete_block(self, block_id: str) -> None:
        self.logger.debug("Deleting block: %s", block_id)
        await self.delete(f"blocks/{block_id}")

    async def get_all_block_children(self, parent_block_id: str) -> list[Block]:
        self.logger.debug("Retrieving all children for block: %s", parent_block_id)

        all_blocks = await paginate_notion_api(self.get_block_children, block_id=parent_block_id)

        self.logger.debug("Retrieved %d total children for block %s", len(all_blocks), parent_block_id)
        return all_blocks

    async def get_block_children(
        self, block_id: str, start_cursor: str | None = None, page_size: int = 100
    ) -> BlockChildrenResponse:
        self.logger.debug("Retrieving children of block: %s", block_id)

        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get(f"blocks/{block_id}/children", params=params)
        return BlockChildrenResponse.model_validate(response)

    async def append_block_children(
        self,
        block_id: str,
        children: list[BlockCreatePayload],
        insert_after_block_id: str | None = None,
    ) -> BlockChildrenResponse | None:
        if not children:
            self.logger.warning("No children provided to append")
            return None

        self.logger.debug("Appending %d children to block: %s", len(children), block_id)

        batches = self._split_into_batches(children)

        if len(batches) == 1:
            children_dicts = self._serialize_blocks(batches[0])
            return await self._send_append_request(block_id, children_dicts, insert_after_block_id)

        return await self._send_batched_append_requests(block_id, batches, insert_after_block_id)

    def _split_into_batches(self, blocks: list[BlockCreatePayload]) -> list[list[BlockCreatePayload]]:
        batches = []
        for i in range(0, len(blocks), self.BATCH_SIZE):
            batch = blocks[i : i + self.BATCH_SIZE]
            batches.append(batch)
        return batches

    def _serialize_blocks(self, blocks: list[BlockCreatePayload]) -> list[dict[str, Any]]:
        return [block.model_dump(exclude_none=True) for block in blocks]

    async def _send_append_request(
        self, block_id: str, children: list[dict[str, Any]], after_block_id: str | None = None
    ) -> BlockChildrenResponse:
        payload = {"children": children}
        if after_block_id:
            payload["after"] = after_block_id

        response = await self.patch(f"blocks/{block_id}/children", payload)
        return BlockChildrenResponse.model_validate(response)

    async def _send_batched_append_requests(
        self, block_id: str, batches: list[list[BlockCreatePayload]], initial_after_block_id: str | None = None
    ) -> BlockChildrenResponse:
        total_blocks = sum(len(batch) for batch in batches)
        self.logger.info("Appending %d blocks in %d batches", total_blocks, len(batches))

        all_responses = []
        after_block_id = initial_after_block_id

        for batch_index, batch in enumerate(batches, start=1):
            self.logger.debug("Processing batch %d/%d (%d blocks)", batch_index, len(batches), len(batch))

            children_dicts = self._serialize_blocks(batch)
            response = await self._send_append_request(block_id, children_dicts, after_block_id)
            all_responses.append(response)

            if response.results:
                after_block_id = response.results[-1].id

            self.logger.debug("Completed batch %d/%d", batch_index, len(batches))

        self.logger.info("Successfully appended all blocks in %d batches", len(batches))
        return self._merge_responses(all_responses)

    def _merge_responses(self, responses: list[BlockChildrenResponse]) -> BlockChildrenResponse:
        if not responses:
            raise ValueError("Cannot merge empty response list - this should never happen")

        first_response = responses[0]
        all_results = [block for response in responses for block in response.results]

        return BlockChildrenResponse(
            object=first_response.object,
            results=all_results,
            next_cursor=None,
            has_more=False,
            type=first_response.type,
            block=first_response.block,
            request_id=responses[-1].request_id,
        )
