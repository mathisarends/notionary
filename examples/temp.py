import logging
from textwrap import dedent
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

        code = dedent(
            """
        ```python
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        print(greet("Mathis"))
        ```
        Caption: Eine einfache Begrüßungsfunktion mit Type Hints
        """
        )
        await page.append_markdown(markdown=code)

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
