import asyncio
from notionary import NotionPage
from notionary.markdown.markdown_builder import MarkdownBuilder


async def main():
    """Minimal column test to isolate parsing issues."""
    
    try:
        page = await NotionPage.from_page_name("Jarvis Clipboard")
        builder = MarkdownBuilder()
        
        builder.h1("Column Test")
        
        # Minimales 2-Column Layout - nur Text
        builder.columns(
            # Column 1
            lambda col: (
                col.h2("Left Column")
                .paragraph("This is simple text in the left column.")
            ),
            # Column 2
            lambda col: (
                col.h2("Right Column") 
                .paragraph("This is simple text in the right column.")
            ),
            width_ratios=[0.7, 0.3]
        )
        
        markdown_content = builder.build()

        print("markdown_content", markdown_content)
        
        print("Generated markdown:")
        print(markdown_content)
        print("=" * 50)
        
        await page.append_markdown(markdown_content)
        print("✅ Success!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())