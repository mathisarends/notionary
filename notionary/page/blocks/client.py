import logging
from typing import Any

from pydantic import TypeAdapter

from notionary.http import HttpClient
from notionary.page.blocks.schemas import (
    Block,
    BlockChildrenResponse,
    BlockCreatePayload,
)
from notionary.shared.decorators import timed

logger = logging.getLogger(__name__)


class BlockClient:
    BATCH_SIZE = 100

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    async def get_block_by_id(self, id: str) -> Block:
        response = await self._client.get(f"blocks/{id}")
        block_adapter = TypeAdapter(Block)
        return block_adapter.validate_python(response)

    async def delete_block(self, block_id: str) -> None:
        logger.debug("Deleting block: %s", block_id)
        await self._client.delete(f"blocks/{block_id}")

    @timed()
    async def get_block_tree(self, block_id: str) -> list[Block]:
        blocks = await self.get_all_block_children(block_id)
        for block in blocks:
            if block.has_children:
                block.children = await self.get_block_tree(block_id=block.id)
        return blocks

    async def get_all_block_children(self, block_id: str) -> list[Block]:
        raw = await self._client.paginate(
            f"blocks/{block_id}/children", method="GET", page_size=100
        )
        block_adapter = TypeAdapter(Block)
        return [block_adapter.validate_python(item) for item in raw]

    async def get_block_children(
        self, block_id: str, start_cursor: str | None = None, page_size: int = 100
    ) -> BlockChildrenResponse:
        params: dict[str, Any] = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor
        response = await self._client.get(f"blocks/{block_id}/children", params=params)
        return BlockChildrenResponse.model_validate(response)

    async def append_block_children(
        self,
        block_id: str,
        children: list[BlockCreatePayload],
        insert_after_block_id: str | None = None,
    ) -> BlockChildrenResponse | None:
        if not children:
            logger.warning("No children provided to append")
            return None

        batches = [
            children[i : i + self.BATCH_SIZE]
            for i in range(0, len(children), self.BATCH_SIZE)
        ]

        if len(batches) == 1:
            return await self._send_append_request(
                block_id, self._serialize_blocks(batches[0]), insert_after_block_id
            )

        return await self._send_batched_append_requests(
            block_id, batches, insert_after_block_id
        )

    def _serialize_blocks(
        self, blocks: list[BlockCreatePayload]
    ) -> list[dict[str, Any]]:
        return [block.model_dump(exclude_none=True) for block in blocks]

    async def _send_append_request(
        self,
        block_id: str,
        children: list[dict[str, Any]],
        after_block_id: str | None = None,
    ) -> BlockChildrenResponse:
        payload: dict[str, Any] = {"children": children}
        if after_block_id:
            payload["after"] = after_block_id
        response = await self._client.patch(f"blocks/{block_id}/children", payload)
        return BlockChildrenResponse.model_validate(response)

    async def _send_batched_append_requests(
        self,
        block_id: str,
        batches: list[list[BlockCreatePayload]],
        initial_after_block_id: str | None = None,
    ) -> BlockChildrenResponse:
        logger.info(
            "Appending %d blocks in %d batches",
            sum(len(b) for b in batches),
            len(batches),
        )

        responses = []
        after_block_id = initial_after_block_id

        for batch in batches:
            response = await self._send_append_request(
                block_id, self._serialize_blocks(batch), after_block_id
            )
            responses.append(response)
            if response.results:
                after_block_id = response.results[-1].id

        return self._merge_responses(responses)

    def _merge_responses(
        self, responses: list[BlockChildrenResponse]
    ) -> BlockChildrenResponse:
        if not responses:
            raise ValueError("Cannot merge empty response list")

        first = responses[0]
        return BlockChildrenResponse(
            object=first.object,
            results=[block for r in responses for block in r.results],
            next_cursor=None,
            has_more=False,
            type=first.type,
            block=first.block,
            request_id=responses[-1].request_id,
        )
