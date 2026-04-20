import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        single_page = await notion.pages.find("ILIAS-CLI")
        await single_page.set_property("Status", "In Bearbeitung")

        batch_page = await notion.pages.find("RTVoice")
        await batch_page.set_properties(
            {
                "Status": "Nicht begonnen",
                "Priorität": "Hoch",
                "Fortschritt": 100,
                "Aufgaben": [
                    "Selected Topics on AI nacharbeiten",
                    "Mathe Fallstudie 12",
                ],
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
