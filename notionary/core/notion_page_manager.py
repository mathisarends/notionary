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
            self.logger.error(f"Error retrieving page content: {result.error}")
            return []
        
        return result.data.get("results", [])
    
    async def get_text(self) -> str:
        """Retrieve the page content and convert it to readable text.
        
        Returns:
            Text representation of the page content
        """
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
    
    markdown = """
# Aufgabenliste für Projekt

## Heute erledigen
- [ ] Dokumentation aktualisieren
- [ ] Meeting-Notizen versenden
- [x] E-Mails beantworten

## Diese Woche
- [ ] Präsentation vorbereiten
- [ ] Code-Review durchführen
- [x] Tests schreiben
- [ ] Feature implementieren mit `speziellem Code`

## Notizen
Hier sind einige wichtige Punkte zu beachten:
* Normale Liste (kein To-do)
* Noch ein Punkt

> Hier ist ein Blockzitat zur Erinnerung:
> Qualität ist wichtiger als Geschwindigkeit!

```python
# Hier ist ein Codeblock
def hello():
    print("Hallo Welt!")
```
    """
    
    
    
    # Append the markdown content to your Notion page
    result = await content_manager.append_markdown(markdown)
    print(result)
    
    # Clean up
    await content_manager.close()
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())