import logging
import asyncio
import traceback
from notionary import NotionPage

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


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
        
        llm = ChatOpenAI(model="gpt-4o-mini")

        base_system_prompt = page.get_notion_markdown_system_prompt()
        human_prompt = "White me a notion Entry about web rtc and its usages for video conferencing with a fitting mermaid diagramm"
        
        response = await llm.ainvoke(
            [
                SystemMessage(content=base_system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        
        print(f"Response: {response.content}")
        
        markdown_appended = await page.append_markdown(markdown=response.content, append_divider=True)
        print(f"Markdown appended: {markdown_appended}")
        

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
