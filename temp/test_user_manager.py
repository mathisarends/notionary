from notionary.user.factories import PersonUserFactory


async def main() -> None:
    factory = PersonUserFactory()
    person = await factory.from_name("Mathis")

    print(person)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
