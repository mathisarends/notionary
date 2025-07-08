import asyncio
from dataclasses import dataclass
from notionary import NotionDatabase

@dataclass  
class OnboardingPageResult:
    url: str
    tile: str
    emoji: str

async def generate_doc_for_database(
    datbase_name: str,
) -> OnboardingPageResult:
    database = await NotionDatabase.from_database_name(datbase_name)
    page = await database.create_blank_page()
    
    page_title = "Welcome to Notionary!"
    page_icon = "📚"
    
    markdown_content = """!> [🚀] This page was created fully automatically and serves as a showcase of what is possible with Notionary.

    ---

    ## 🗃️ Working with Databases

    Discover and manage your Notion databases programmatically:

    ```python
    import asyncio
    from notionary import NotionDatabase, DatabaseDiscovery

    async def main():
    # Discover available databases
    discovery = DatabaseDiscovery()
    await discovery()

    # Connect to a database by name
    db = await NotionDatabase.from_database_name("Projects")

    # Create a new page in the database
    page = await db.create_blank_page()

    # Query pages from database
    async for page in db.iter_pages():
        title = await page.get_title()
        print(f"Page: {title}")

    if __name__ == "__main__":
    asyncio.run(main())
    ```

    ## 📄 Creating and Managing Pages
    Create and update Notion pages with rich content:
    ```python
    import asyncio
    from notionary import NotionPage

    async def main():
        # Create a page from URL
        page = NotionPage.from_url("https://www.notion.so/your-page-url")

        # Or find by name
        page = await NotionPage.from_page_name("My Project Page")

        # Update page metadata
        await page.set_title("Updated Title")
        await page.set_emoji_icon("🚀")
        await page.set_random_gradient_cover()

        # Add markdown content
        markdown = '''
        # Project Overview

        !> [💡] This page was created programmatically using Notionary.

        ## Features
        - **Rich** Markdown support
        - Async functionality
        - Custom syntax extensions
        '''

        await page.replace_content(markdown)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

    ## 📊 Tables and Structured Data
    Create tables for organizing information:
    FeatureStatusPriorityAPI IntegrationCompleteHighDocumentationIn ProgressMediumDatabase QueriesCompleteHighFile UploadsCompleteMedium

    🎥 Media Embedding
    Embed videos directly in your pages:
    @[Caption](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - Never gonna give you up!

    Happy building with Notionary! 🎉"""

    
    await page.set_title(page_title)
    await page.set_emoji_icon(page_icon)
    await page.set_random_gradient_cover()
    await page.append_markdown(markdown_content)
    
    url = await page.get_url()
    
    return OnboardingPageResult(
        url=url,
        tile=page_title,
        emoji=page_icon,
    )
    
    
if __name__ == "__main__":
    print("🚀 Starting Notionary onboarding page generation...")
    result = asyncio.run(generate_doc_for_database("Wissen & Notizen"))
    print(f"✅ Onboarding page created: {result.tile} {result.emoji} - {result.url}")