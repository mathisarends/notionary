from typing import Any, Dict, List, Optional
from notionary.converters.markdown_to_notion_converter import MarkdownToNotionConverter
from notionary.converters.notion_to_markdown_converter import NotionToMarkdownConverter
from notionary.core.notion_client import NotionClient
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
    
    async def get_text(self) -> str:
        """Retrieve the page content and convert it to readable text.
        
        Args:
            include_table_data: Whether to include data from tables (requires additional API calls)
            
        Returns:
            Text representation of the page content
        """
        blocks = await self.get_page_blocks_with_children()
        return NotionToMarkdownConverter.convert(blocks)

    
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
    
    markdown = """# Beispiel mit Codeblöcken und Tabellen

Hier ist ein Codeblock in Python:

```python
def greet(name):
    return f"Hallo, {name}!"

print(greet("Mathis"))
```
<!-- spacer -->

## Tabelle mit Daten

| Name  | Alter | Beruf         |
| ----- | ----- | ------------- |
| Anna  | 29    | Designerin    |
| Ben   | 35    | Entwickler    |
| Clara | 41    | Projektleiterin |

## Weitere Sektion

!> [🚧] Dies ist ein Callout mit einem Hinweistext

---

## Video Embed Beispiel

Hier ist ein eingebettetes Video von YouTube:

@[Einführung in Python-Programmierung](https://www.youtube.com/watch?v=rfscVS0vtbw)

Und ein weiteres Video ohne Beschriftung:

@[](https://vimeo.com/148751763)

---

## Noch ein Codeblock – JSON

```json
{
"name": "Mathis",
"projekte": ["Notion", "Automation"],
"aktiv": true
}
```
<!-- spacer -->
<!-- spacer -->

## Toggle Inhalt

Auch hier ist etwas Inhalt in einem Toggle versteckt.

```bash
echo "Toggle mit Codeblock"
```

## Aufgabenliste

- [ ] Implementierung des TodoElement abschließen
- [x] Markdown-Parser überprüfen
- [ ] Tabellen-Element testen
- [ ] Code-Block-Formatierung optimieren
- [x] Callout-Elemente unterstützen
- [ ] Dokumentation aktualisieren
- [ ] Unit-Tests für alle Element-Typen schreiben
- [x] Element-Registry implementieren
- [ ] Integration mit Notion API testen
- [ ] Regressionstests durchführen

## Formatierungsbeispiele

Hier folgen einige **Formatierungsbeispiele** zum Testen:

1. **Fettgedruckter** Text mit `Code-Snippet` darin
2. *Kursiver* Text mit __unterstrichenem__ Abschnitt
3. ~~Durchgestrichener~~ Text mit **_gemischter Formatierung_**
4. Hervorhebungen in ==yellow:Gelb== und ==blue:Blau==
5. Ein [Link mit **Formatierung**](https://notion.so) darin
6. Verschachtelte `Formatierungen` mit *`gemischten`* **Stilen**
7. Text mit ==red_background:farbigem Hintergrund==

## Farbige Blockzitate

> [background:brown] Dies ist ein Blockzitat mit braunem Hintergrund.
> Es kann mehrere Zeilen enthalten.

Bla Bla

> [color:yellow] Und hier ist ein gelbes Blockzitat.
> Mit mehreren Absätzen.
<!-- spacer -->

Bla Bla

[bookmark](https://claude.ai/chat/a241fdb4-6526-4e0e-9a9f-c4573e7e834d "Beispieltitel")

## Bilder und Videos

Hier ist ein Bild mit Beschriftung:
![Ein schönes Landschaftsbild](https://images.unsplash.com/photo-1506744038136-46273834b3fb)

Und hier noch ein direkt eingebettetes Video:
@[Ein Naturdokumentarfilm](https://example.com/naturvideo.mp4)
"""

    markdown_yt = """# YouTube Video Embeds in Columns
::: columns
::: column
## Standard YouTube URL
@[Learn Python - Full Course for Beginners](https://www.youtube.com/watch?v=rfscVS0vtbw)
:::
::: column
## YouTube Shortened URL
@[Python Tutorial](https://youtu.be/Z1Yd7upQsXY)
:::
::: column
## YouTube URL without Caption
@[](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
:::
:::

## Toggle Section Below

+++ Toggle title
    Indented content that belongs to the toggle
    More indented content

+++ Empty Toggle

## Videos With Toggles in Columns

::: columns
::: column
### Video with Toggle
@[Python Tips](https://www.youtube.com/watch?v=C-gEQdGVXbk)

+++ Toggle Details
    This video contains good Python tips
    for beginners and advanced users
:::
::: column
### Another Video with Toggle
@[Data Science](https://youtu.be/ua-CiDNNj30)

+++ Video Description
    Learn about data science
    and pandas library in Python
:::
:::
"""
    try:
        # Retrieve the text with table data
        blocks = await content_manager.append_markdown(markdown_text=markdown_yt)
        print(blocks)
    finally:
        # Clean up
        await content_manager.close()
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())