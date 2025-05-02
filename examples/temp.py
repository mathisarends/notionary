"""
# Notionary: Page Lookup Example
===============================

This example demonstrates how to locate an existing Notion page
using the NotionPageFactory.

It showcases the easiest way to access a page by its name,
but also mentions alternatives like lookup by ID or URL.

IMPORTANT: Replace "Jarvis fitboard" with the actual name of your page.
The factory uses fuzzy matching to find the closest match.
"""

import asyncio
from notionary import NotionPageFactory

YOUR_PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demonstrates various ways to find a Notion page."""

    try:
        print("Searching for page by name...")
        page = await NotionPageFactory.from_page_name(YOUR_PAGE_NAME)

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )

        print(f'✅ Found: "{title}" {icon} → {url}')

        markdown_content = """
 Stresstest für Quote Element

Normaler Text vor einem Zitat.

> Ein einfaches, einzeiliges Zitat.

Etwas normaler Text zwischen den Zitaten.

> Ein mehrzeiliges Zitat
> das über mehrere Zeilen geht
> mit drei Zeilen insgesamt.

Text nach einem mehrzeiligen Zitat.

> Zitat mit **Markdown-Formatierung** und *kursivem Text*
> und auch einem [Link](https://example.com)

Text zwischen komplizierten Zitaten.

> Zitat mit einer leeren Zeile
> 
> Die durch eine Leerzeile getrennt werden sollte.

Ein weiterer normaler Abschnitt.

> Zitat mit verschachtelten Listen:
> - Erster Punkt
> - Zweiter Punkt
>   - Unterpunkt 2.1
>   - Unterpunkt 2.2
> - Dritter Punkt

Text vor eingerücktem Zitat.

   > Ein eingerücktes Zitat
   > mit mehreren Zeilen
   > die alle eingerückt sind.

Text vor Zitat-Edge-Cases.

>Zitat ohne Leerzeichen nach >
>und mehrere solche Zeilen
>sollte trotzdem funktionieren

Ein Abschnitt vor gemischten Formatierungen.

> # Überschrift in einem Zitat
> 
> Mit Text darunter und einer
> ```
> Codeblock innerhalb des Zitats
> Mit mehreren Zeilen Code
> ```
> Und noch mehr Text danach.

Test für nebeneinander liegende Zitate:

> Erstes Zitat

> Zweites Zitat direkt danach
> mit mehreren Zeilen

> Drittes Zitat mit nur einer Leerzeile Abstand

Nicht zusammenhängende Zitate:

> Zitat A

Normaler Text.

> Zitat B

Tests für verschachtelte Zitate:

> Äußeres Zitat
> > Verschachteltes Zitat
> > mit mehreren Zeilen
> Zurück zum äußeren Zitat

Abschließender Text.
        
        """

        await page.append_markdown(markdown_content)


    except Exception as e:
        print(f"❌ Error while loading page from URL: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    found_page = asyncio.run(main())
