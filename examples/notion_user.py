"""
Minimal example for using NotionUser.from_name()
"""

import asyncio
from notionary import NotionUser

SEARCH_NAME = "YOUR_NOTION_USER_NAME"  # Replace with your own user name


async def example_from_name():
    """Example: Create NotionUser from name using fuzzy matching"""
    print("=== NotionUser.from_name Example ===")

    try:
        user = await NotionUser.from_name(SEARCH_NAME)

        if user:
            print("✅ Found user by name:")
            print(f"   Searched for: '{SEARCH_NAME}'")
            print(f"   Found: '{user.name}'")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")

    except ValueError as e:
        print(f"❌ No suitable user found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run the example"""
    await example_from_name()


if __name__ == "__main__":
    asyncio.run(main())
