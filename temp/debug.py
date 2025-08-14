from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    # Füge einen Toggle-Block mit einer Tabelle im Inneren hinzu
    result = await page.append_markdown(
        lambda builder: builder.toggle(
            "📋 Clipboard Tabelle",
            lambda t: t.table(
                headers=["Spalte A", "Spalte B"],
                rows=[["Wert 1", "Wert 2"], ["Wert 3", "Wert 4"]],
            ),
        )
    )

    print("result", result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
