import logging
import asyncio
import traceback
from notionary import NotionPage


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.from_page_name("Jarvis Clipboard")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f"Page found: {page.id}")
        print(f"{icon} → {title} → {url}")

        markdown = """
        Dies ist ein Text mit Einrückung.
        - Punkt 1 mit Einrückung
            - Unterpunkt mit noch mehr Einrückung

        ```python
        def hello_world():
            print("Hello, World!")
            if True:
                print("Eingerückt!")
        ```
        
        !> This should demonstrate a callout element.
        """        
        
        markdown_appended = await page.append_markdown(markdown=markdown, append_divider=True)
        print(f"Markdown appended: {markdown_appended}")
        

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
