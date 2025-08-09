from notionary import NotionPage


async def main():
    # Hole die Seite über ihren Namen
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    # Table of contents, Standardfarbe
    toc_block = """
[toc](blue_background)

# Test 123
Dies ist ein **fettgedrucktes** Wort, hier *kursiv*, und hier `Code`.
Außerdem ein [Link](https://example.com) und ~~durchgestrichen~~.
    """


    # Block anhängen + Divider danach
    await page.append_markdown(toc_block, append_divider=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
