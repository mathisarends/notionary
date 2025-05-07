import json
from typing import Any, Dict, List, Optional

from notionary.elements.divider_element import DividerElement
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
    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: BlockElementRegistry,
    ):
        self.page_id = page_id
        self._client = client
        self.block_registry = block_registry
        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self._chunker = NotionPageContentChunker()


    async def append_markdown(self, markdown_text: str, append_divider = False) -> bool:
        """
        Append markdown text to a Notion page, automatically handling content length limits.

        """
        if append_divider and not self.block_registry.contains(DividerElement):
            self.logger.warning(
                "DividerElement not registered. Appending divider skipped."
            )
            append_divider = False
            
        # Append divider in markdonw format as it will be converted to a Notion divider block
        if append_divider:
            markdown_text = markdown_text + "\n\n---\n\n"
        
        try:
            blocks = self._markdown_to_notion_converter.convert(markdown_text)
            fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

            result = await self._client.patch(
                f"blocks/{self.page_id}/children", {"children": fixed_blocks}
            )
            return bool(result)
        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e))
            return False
            
        
    async def clear_page_content(self) -> bool: 
        """ 
        Clear all content of the page.
        """ 
        try:
            blocks_resp = await self._client.get(f"blocks/{self.page_id}/children") 
            results = blocks_resp.get("results", []) if blocks_resp else [] 
    
            if not results:
                return True
            
            success = True
            for block in results: 
                block_success = await self.delete_block_with_children(block)
                if not block_success:
                    success = False
            
            return success
        except Exception as e: 
            self.logger.error("Error clearing page content: %s", str(e)) 
            return False
                    
    
    async def delete_block_with_children(self, block: Dict[str, Any]) -> bool: 
        """ 
        Delete a block and all its children.
        """ 
        try: 
            if block.get("has_children", False): 
                children_resp = await self._client.get(f"blocks/{block['id']}/children") 
                child_results = children_resp.get("results", [])
                
                for child in child_results: 
                    child_success = await self.delete_block_with_children(child)
                    if not child_success:
                        return False

            return await self._client.delete(f"blocks/{block['id']}")
        except Exception as e: 
            self.logger.error("Failed to delete block: %s", str(e)) 
            return False

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
