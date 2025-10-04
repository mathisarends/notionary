from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    ### Content-Plan für Social Media

    |           Thema            |  Plattform  |    Status   | Veröffentlichungsdatum |
    | -------------------------- | ----------- | ----------- | ---------------------- |
    | Herbst-Special Ankündigung |  Instagram  | In Arbeit 🚧 |       2025-10-15       |
    |    Neues Feature-Video     |   YouTube   |  Geplant 🗓️ |       2025-10-22       |
    |   Wochenend-Rabattaktion   |   Facebook  |   Fertig ✅  |       2025-10-04       |
    |      Blog-Post Teaser      | Twitter / X |  Geplant 🗓️ |       2025-10-28       |
    |      @user[Mathis Arends]      |   LinkedIn  | In Arbeit 🚧 |       2025-11-05       |

    """
    content = await page.append_markdown(markdown)
    print("content", content)

    content = await page.get_markdown_content()
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
