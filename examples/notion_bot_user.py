"""
Minimal example for using NotionBotUser.from_name()
"""

import asyncio
from notionary.user.notion_bot_user import NotionBotUser

SEARCH_NAME = "VoiceAssistent"  # Replace with your bot name


async def example_from_name():
    """Example: Create NotionBotUser from name using fuzzy matching"""
    print("=== NotionBotUser.from_name Example ===")

    try:
        bot_user = await NotionBotUser.from_current_bot(SEARCH_NAME)

        if bot_user:
            print("✅ Found bot user by name:")
            print(f"   Searched for: '{SEARCH_NAME}'")
            print(f"   Found: '{bot_user.name}'")
            print(f"   ID: {bot_user.id}")
            print(f"   Workspace: '{bot_user.workspace_name}'")
            print(f"   Owner Type: {bot_user.owner_type}")
            print(f"   Max Upload: {bot_user.max_file_upload_size / (1024*1024):.2f} MB")

    except ValueError as e:
        print(f"❌ No suitable bot user found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run the example"""
    await example_from_name()


if __name__ == "__main__":
    asyncio.run(main())
