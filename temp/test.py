from notionary import NotionPage


async def main():
    # Hole die Seite über ihren Namen
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    page.block_element_registry = (
        page.block_registry_builder.without_bulleted_list().build()
    )

    # Table of contents, Standardfarbe
    toc_block = """
[toc](blue_background)

# Test 123
Dies ist ein **fettgedrucktes** Wort, hier *kursiv*, und hier `Code`.
Außerdem ein [Link](https://example.com) und ~~durchgestrichen~~.

Siehe Seite: @[248389d5-7bd3-8193-8dc3-ea10c22502f1]
    """

    # Block anhängen + Divider danach
    await page.replace_content(toc_block)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
