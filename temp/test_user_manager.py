from notionary.user.notion_person import NotionPersonFactory


async def main() -> None:
    # Instanz erstellen
    factory = NotionPersonFactory()

    # Methode auf der Instanz aufrufen
    person = await factory.from_name("Mathis")

    print(person)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
