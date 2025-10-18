import asyncio

from notionary import NotionPage

# Replace with your desired page title
PAGE_TITLE = "SOME PAGE"


async def main() -> None:
    page = await NotionPage.from_title(PAGE_TITLE)
    print(f"Found page: {page.title} (URL: {page.url})")

    content = await page.get_markdown_content()
    print("Page content in Markdown:")
    print(content)

    markdown_to_append = """
    ## Appended Section
    # This section was appended to the page using Notionary!
    - It supports bullet points
    - and other stuff
    """

    await page.append_markdown(markdown_to_append)

    print("Look at the page at ", page.url, "to see your content added.")


if __name__ == "__main__":
    asyncio.run(main())
