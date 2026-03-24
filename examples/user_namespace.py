import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        me = await notion.users.me()
        print(f"Bot: {me.name} ({me.workspace_name})")

        users = await notion.users.list_users()
        for user in users:
            print(f"  {user.name} – {user.email}")

        results = await notion.users.search("mathis")
        for user in results:
            print(f"  Found: {user.name}")

        user = await notion.users.get(users[0].id)
        print(user)


if __name__ == "__main__":
    asyncio.run(main())
