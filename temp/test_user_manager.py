from notionary.user.person import PersonUser


async def main() -> None:
    person = await PersonUser.from_name("Mathis")
    print(person)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
