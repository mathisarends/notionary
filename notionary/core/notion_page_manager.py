from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.notion_content_converter import NotionContentConverter
from notionary.core.markdown_to_notion import MarkdownToNotionConverter
from notionary.util.logging_mixin import LoggingMixin


class NotionPageContentManager(LoggingMixin):
    """Class for managing Notion page content (text and blocks)."""
    
    def __init__(self, page_id: str, token: Optional[str] = None):
        """Initialize the NotionContentManager.
        
        Args:
            page_id: ID of the Notion page
            token: Notion API Token (optional)
        """
        self._client = NotionClient(token=token)
        self.page_id = page_id
        
    async def append_markdown(self, markdown_text: str) -> str:
        """Append markdown text to the page.
        
        Args:
            markdown_text: Markdown-formatted text
            
        Returns:
            Status message about the operation result
        """
        notion_markdown_converter = MarkdownToNotionConverter()
        content_blocks = notion_markdown_converter.convert(markdown_text=markdown_text)
        
        data = {
            "children": content_blocks
        }
        
        result = await self._client.patch(f"blocks/{self.page_id}/children", data)
        
        if result:
            self.logger.info("Successfully added text to the page.")
            return "Successfully added text to the page."
        else:
            return f"Error adding text to the page: {result.error}"
    
    async def get_blocks(self) -> List[Dict[str, Any]]:
        """Retrieve the page content as blocks.
        
        Returns:
            List of block objects or empty list on error
        """
        result = await self._client.get(f"blocks/{self.page_id}/children")
        
        if not result:
            self.logger.error("Error retrieving page content: %s", result.error)
            return []
        
        return result.data.get("results", [])
    
    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        """Retrieve the children of a specific block (e.g., table rows).
        
        Args:
            block_id: ID of the parent block
            
        Returns:
            List of child block objects or empty list on error
        """
        result = await self._client.get(f"blocks/{block_id}/children")
        
        if not result:
            self.logger.error("Error retrieving block children: %s", result.error)
            return []
        
        return result.data.get("results", [])
    
    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        """Retrieve the page content as blocks, including children for blocks that have them.
        
        This is useful for tables and other nested block structures.
        
        Returns:
            List of block objects with their children or empty list on error
        """
        # Get the main blocks
        blocks = await self.get_blocks()
        
        # For each block that may have children (has_children=True),
        # fetch its children and add them to the block
        for block in blocks:
            if block.get("has_children", False):
                block_id = block.get("id")
                if block_id:
                    children = await self.get_block_children(block_id)
                    if children:
                        block["children"] = children
        
        return blocks
    
    async def get_text(self, include_table_data: bool = True) -> str:
        """Retrieve the page content and convert it to readable text.
        
        Args:
            include_table_data: Whether to include data from tables (requires additional API calls)
            
        Returns:
            Text representation of the page content
        """
        if include_table_data:
            # Holen aller Blöcke mit Kindern und Konvertierung mit der erweiterten converter-Methode
            blocks = await self.get_page_blocks_with_children()
            return NotionContentConverter.blocks_to_text(blocks, include_table_data=True)
        else:
            # Normale Konvertierung ohne zusätzliche Daten
            blocks = await self.get_blocks()
            return NotionContentConverter.blocks_to_text(blocks)
    
    async def clear(self) -> str:
        """Delete all content from the page.
        
        Returns:
            Status message about the operation result
        """
        blocks = await self.get_blocks()
        
        if not blocks:
            return "No content to delete or error retrieving content."
        
        # Delete each block individually
        deleted_count = 0
        for block in blocks:
            block_id = block.get("id")
            if not block_id:
                continue
                
            result = await self._client.delete(f"blocks/{block_id}")
            
            if result:
                deleted_count += 1
        
        if deleted_count == len(blocks):
            self.logger.info("Successfully deleted all %d blocks from the page.", deleted_count)
            return f"Successfully deleted all {deleted_count} blocks from the page."
        else:
            self.logger.warning("Partially cleared page. Deleted %d out of %d blocks.", deleted_count, len(blocks))
            return f"Partially cleared page. Deleted {deleted_count} out of {len(blocks)} blocks."
    
    async def replace_content(self, markdown_text: str) -> str:
        """Clear page content and replace it with new markdown text.
        
        Args:
            markdown_text: New markdown-formatted content
            
        Returns:
            Status message about the operation result
        """
        results = []
        
        clear_result = await self.clear()
        results.append(clear_result)
        
        append_result = await self.append_markdown(markdown_text)
        results.append(append_result)
        
        return "\n".join(results)
    
    async def close(self):
        """Close the client connection properly."""
        await self._client.close()


async def demo():
    """Example usage of the NotionContentManager."""
    content_manager = NotionPageContentManager(page_id="1a3389d5-7bd3-80d7-a507-e67d1b25822c")
    
    markdown = """# Page with Callouts

Regular paragraph text.

!> Simple callout with default emoji and color

!> [🤖] J.A.R.V.I.S Creative Space

!> {gray_background} [🤖] J.A.R.V.I.S Creative Space with gray background

>> A toggle block with a callout inside

  !> [🔍] Nested callout inside a toggle
  
  Regular content inside the toggle

# More content

Another paragraph after the callouts."""
    
    
    try:
        # Retrieve the text with table data
        text_with_tables = await content_manager.get_blocks()
        print(text_with_tables)
    finally:
        # Clean up
        await content_manager.close()
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())