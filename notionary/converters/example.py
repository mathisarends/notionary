from notionary.converters import MarkdownToNotionConverter
from notionary.core.notion_client import NotionClient

async def append_markdown(page_id: str, markdown_text: str) -> str:
    notion_client = NotionClient()
    notion_markdown_converter = MarkdownToNotionConverter()
    content_blocks = notion_markdown_converter.convert(markdown_text=markdown_text)
        
    data = {
        "children": content_blocks
    }
        
    result = await notion_client.patch(f"blocks/{page_id}/children", data)
        
    if result:
        print("Successfully added text to the page.")

async def demo():
    """Example usage of the NotionContentManager."""
    page_id = "1a3389d5-7bd3-80d7-a507-e67d1b25822c"
    
    markdown = """# Document with Dividers

This is the first section of content.

---

## Second Section

Content after a divider.

!> [💡] Callout block in the second section

***

### Third Section

Content in the third section.

>> Toggle Section

  Content inside a toggle.
  
  ---
  
  Even toggles can contain dividers!
"""
    
    await append_markdown(page_id=page_id, markdown_text=markdown)
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())