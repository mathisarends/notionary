from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    equation = """
[equation](x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a})
    """

    await page.append_markdown(equation, append_divider=True)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())