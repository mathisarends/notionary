"""
# Notionary: Rich Notion Page Example
=========================================

This example demonstrates how to create a feature-rich Notion page using the NotionPageManager
and custom Markdown extensions supported by Notionary.

## Features
- Connect to a Notion page using its URL
- Update page properties and metadata (title, icon, cover)
- Create rich content using custom Markdown syntax
- Showcase various Notion blocks (callouts, toggles, etc.)
"""

import asyncio
from notionary.core.page.notion_page_manager import NotionPageManager
from examples.ressources.markdown_demo import markdown_example_rich_text


async def main():
    """Create a rich Notion page showcasing various content blocks."""
    
    url = "https://www.notion.so/Notionary-Rich-Markdown-Demo-1cd389d57bd381e58be9d35ce24adf3d?pvs=4"
    
    page_manager = NotionPageManager(url=url)
    
    try:
        print("🎨 Setting page metadata...")
        await page_manager.set_title("Notionary Rich Markdown Demo")
        await page_manager.set_page_icon(emoji="✨")
        await page_manager.set_page_cover("https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200")
    
        
        print("✨ Updating page with rich content...")
        await page_manager.replace_content(markdown_example_rich_text)
        
        print("🎉 Page updated successfully with rich content!")
        print("🔗 Open the page in Notion to see the results")
        
    except Exception as e:
        print(f"❌ Error updating page: {e}")
    finally:
        await page_manager.close()


if __name__ == "__main__":
    asyncio.run(main())