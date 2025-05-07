import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

from notionary.elements.registry.block_element_registry import BlockElementRegistry
from notionary.notion_client import NotionClient

from notionary.page.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.page.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.page.content.notion_page_content_chunker import (
    NotionPageContentChunker,
)
from notionary.util.logging_mixin import LoggingMixin


class PageContentManager(LoggingMixin):
    BATCH_SIZE = 100

    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: Optional[BlockElementRegistry] = None,
    ):
        self.page_id = page_id
        self._client = client
        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self._chunker = NotionPageContentChunker()

    async def append_markdown(self, markdown_text: str, append_divider=False) -> str:
        """
        Append markdown text to a Notion page, automatically handling content length limits.

        Args:
            markdown_text: The markdown text to append
            append_divider: If True, appends a divider after the markdown content (default: False)
        """
        try:
            # Just the markdown synthax for the divider as it will be converted to a Notion divider block
            if append_divider:
                markdown_text = markdown_text + "\n\n---\n\n"

            blocks = self._markdown_to_notion_converter.convert(markdown_text)
            fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

            total_blocks = len(fixed_blocks)
            num_batches = (total_blocks + self.BATCH_SIZE - 1) // self.BATCH_SIZE

            all_success = True
            for batch_num in range(num_batches):
                start_idx = batch_num * self.BATCH_SIZE
                end_idx = min((batch_num + 1) * self.BATCH_SIZE, total_blocks)
                batch = fixed_blocks[start_idx:end_idx]

                batch_success = await self._process_batch(batch, batch_num, num_batches)
                if not batch_success:
                    all_success = False
                    break

            if all_success:
                return f"Successfully added {total_blocks} blocks to the page in {num_batches} batch(es)."
            return "Failed to add all blocks. See logs for details."

        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e))
            raise

    async def has_database_descendant(self, block_id: str) -> bool:
        """
        Check if a block or any of its descendants is a database.
        """
        resp = await self._client.get(f"blocks/{block_id}/children")
        children = resp.get("results", []) if resp else []

        for child in children:
            block_type = child.get("type")
            if block_type in ["child_database", "database", "linked_database"]:
                return True

            if child.get("has_children", False):
                if await self.has_database_descendant(child["id"]):
                    return True

        return False

    async def delete_block_with_children(
        self, block: Dict[str, Any], skip_databases: bool
    ) -> Tuple[int, int]:
        """
        Delete a block and all its children, optionally skipping databases.
        Returns a tuple of (deleted_count, skipped_count).
        """
        deleted = 0
        skipped = 0

        block_type = block.get("type")
        if skip_databases and block_type in [
            "child_database",
            "database",
            "linked_database",
        ]:
            return 0, 1

        # Process children in parallel
        if block.get("has_children", False):
            children_resp = await self._client.get(f"blocks/{block['id']}/children")
            children = children_resp.get("results", [])
            
            if children:
                # Process all children in parallel
                tasks = [self.delete_block_with_children(child, skip_databases) 
                        for child in children]
                results = await asyncio.gather(*tasks)
                
                for child_deleted, child_skipped in results:
                    deleted += child_deleted
                    skipped += child_skipped

        # Then delete the block itself
        if await self._client.delete(f"blocks/{block['id']}"):
            deleted += 1

        return deleted, skipped

    async def clear(self, skip_databases: bool = True, batch_size: int = 10) -> str:
        """
        Clear the content of the page in parallel, optionally preserving databases.
        
        Args:
            skip_databases: If True, will not delete databases or blocks containing databases
            batch_size: Number of blocks to process in parallel
            
        Returns:
            A string describing how many blocks were deleted and skipped
        """
        # Get all top-level blocks
        blocks_resp = await self._client.get(f"blocks/{self.page_id}/children")
        results = blocks_resp.get("results", []) if blocks_resp else []
        
        if not results:
            return "No blocks to delete."
        
        first_result = results[0] if results else None
        print("first_result", json.dumps(first_result, indent=4))

        total_deleted = 0
        total_skipped = 0
        
        # Process blocks in batches to avoid overwhelming the API
        for i in range(0, len(results), batch_size):
            batch = results[i:i + batch_size]
            
            # Pre-check which blocks have databases if needed
            if skip_databases:
                has_db_tasks = [self.has_database_descendant(block["id"]) for block in batch]
                has_database = await asyncio.gather(*has_db_tasks)
            else:
                has_database = [False] * len(batch)
            
            # Create tasks for blocks that don't have databases (if skipping)
            tasks = []
            skip_indices = []
            
            for j, block in enumerate(batch):
                block_type = block.get("type")
                skip_this_block = (skip_databases and 
                                (block_type in ["child_database", "database", "linked_database"] or 
                                has_database[j]))
                
                if skip_this_block:
                    skip_indices.append(j)
                else:
                    tasks.append(self.delete_block_with_children(block, skip_databases))
            
            # Process deletion tasks in parallel
            if tasks:
                results = await asyncio.gather(*tasks)
                for deleted, skipped in results:
                    total_deleted += deleted
                    total_skipped += skipped
            
            # Count skipped blocks
            total_skipped += len(skip_indices)
            
            # Log progress
            self.logger.info(
                f"Processed batch {i//batch_size + 1}/{(len(results) + batch_size - 1)//batch_size}: "
                f"Deleted {total_deleted} blocks, skipped {total_skipped} blocks so far."
            )
        
        return f"Deleted {total_deleted} blocks. Skipped {total_skipped} database blocks."

    async def get_blocks(self) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{self.page_id}/children")
        if not result:
            self.logger.error("Error retrieving page content: %s", result.error)
            return []
        return result.get("results", [])

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{block_id}/children")
        if not result:
            self.logger.error("Error retrieving block children: %s", result.error)
            return []
        return result.get("results", [])

    async def get_page_blocks_with_children(
        self, parent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        blocks = (
            await self.get_blocks()
            if parent_id is None
            else await self.get_block_children(parent_id)
        )

        if not blocks:
            return []

        for block in blocks:
            if not block.get("has_children"):
                continue

            block_id = block.get("id")
            if not block_id:
                continue

            # Recursive call for nested blocks
            children = await self.get_page_blocks_with_children(block_id)
            if children:
                block["children"] = children

        return blocks

    async def get_text(self) -> str:
        blocks = await self.get_page_blocks_with_children()
        return self._notion_to_markdown_converter.convert(blocks)

    async def _process_batch(
        self, batch: List[Dict], batch_num: int, num_batches: int
    ) -> bool:
        """
        Verarbeitet einen einzelnen Batch von Blöcken und gibt zurück, ob es erfolgreich war.
        """
        result = await self._client.patch(
            f"blocks/{self.page_id}/children", {"children": batch}
        )

        if not result:
            self.logger.error(
                "Failed to add batch %d/%d to page.", batch_num + 1, num_batches
            )
            return False

        self.logger.info(
            "Successfully added batch %d/%d (%d blocks) to page.",
            batch_num + 1,
            num_batches,
            len(batch),
        )
        return True
