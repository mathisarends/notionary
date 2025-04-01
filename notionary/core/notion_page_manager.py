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
    
    async def get_text(self, include_table_data: bool = False) -> str:
        """Retrieve the page content and convert it to readable text.
        
        Args:
            include_table_data: Whether to include data from tables (requires additional API calls)
            
        Returns:
            Text representation of the page content
        """
        if include_table_data:
            blocks = await self.get_page_blocks_with_children()
            
            # Wir verwenden hier die selbst implementierte Funktion, die mit den 
            # bereits abgerufenen Kindern arbeitet, anstatt sie einzeln zu laden
            return self.blocks_to_text_with_table_data(blocks)
        else:
            blocks = await self.get_blocks()
            return NotionContentConverter.blocks_to_text(blocks)
    
    def blocks_to_text_with_table_data(self, blocks: List[Dict[str, Any]]) -> str:
        """Convert blocks to text, including data from table children if present.
        
        Args:
            blocks: List of block objects, potentially with 'children' attributes
            
        Returns:
            Text representation of the blocks
        """
        # Zunächst normal konvertieren
        text = NotionContentConverter.blocks_to_text(blocks)
        
        # Nur wenn Tabellenplatzhalter vorhanden sind, diese ersetzen
        for block in blocks:
            if block.get("type") == "table" and "children" in block:
                # Platzhalter-Tabelle generieren (gleiche Logik wie im TableConverter)
                table_data = block.get("table", {})
                table_width = table_data.get("table_width", 3)
                placeholder_table = self._generate_placeholder_table(table_width)
                
                # Vollständige Tabelle mit vorhandenen Kindern erstellen
                full_table = self._process_table_with_children(block, block.get("children", []))
                
                # Platzhalter durch die vollständige Tabelle ersetzen
                if full_table and placeholder_table in text:
                    text = text.replace(placeholder_table, full_table)
        
        return text
    
    def _generate_placeholder_table(self, table_width: int) -> str:
        """Generiert eine Platzhalter-Tabelle mit der angegebenen Breite."""
        header_cells = [f"Spalte {i+1}" for i in range(table_width)]
        header_row = "| " + " | ".join(header_cells) + " |"
        separator_row = "| " + " | ".join(["---" for _ in range(table_width)]) + " |"
        placeholder_row = "| " + " | ".join(["..." for _ in range(table_width)]) + " |"
        
        return f"{header_row}\n{separator_row}\n{placeholder_row}"
    
    def _process_table_with_children(self, 
                                    table_block: Dict[str, Any], 
                                    row_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Verarbeitet einen Tabellen-Block mit seinen Kinder-Blöcken."""
        if not row_blocks:
            return None
            
        table_data = table_block.get("table", {})
        has_column_header = table_data.get("has_column_header", False)
        
        table_rows = []
        column_count = 0
        
        # Jede Zeile verarbeiten
        for i, row_block in enumerate(row_blocks):
            if row_block.get("type") != "table_row":
                continue
                
            row_data = row_block.get("table_row", {})
            cells = row_data.get("cells", [])
            
            # Maximale Spaltenzahl für den Separator ermitteln
            if len(cells) > column_count:
                column_count = len(cells)
            
            # Zellen in Text konvertieren
            row_texts = []
            for cell in cells:
                cell_text = NotionContentConverter.extract_text_with_formatting(cell)
                row_texts.append(cell_text or "")
            
            # Zeile als Tabelle formatieren
            row = "| " + " | ".join(row_texts) + " |"
            table_rows.append(row)
        
        # Wenn keine Zeilen gefunden wurden, None zurückgeben
        if not table_rows or column_count == 0:
            return None
            
        # Header-Trenner hinzufügen, wenn es sich um eine Tabellenüberschrift handelt
        if has_column_header and len(table_rows) > 0:
            separator_row = "| " + " | ".join(["---" for _ in range(column_count)]) + " |"
            table_rows.insert(1, separator_row)
            
        return "\n".join(table_rows)
    
    async def get_text_with_tables(self) -> str:
        """Vereinfachte Methode, die direkt Text mit Tabellendaten zurückgibt."""
        return await self.get_text(include_table_data=True)
    
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
    
    # Retrieve the text with table data
    text_with_tables = await content_manager.get_text_with_tables()
    print(text_with_tables)
    
    # Clean up
    await content_manager.close()
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())