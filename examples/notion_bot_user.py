"""
Minimal example for using NotionBotUser.from_current_integration()
"""

import asyncio
from notionary import NotionBotUser


async def example_from_current_integration():
    """Example: Create NotionBotUser from the current integration"""
    print("=== NotionBotUser.from_current_integration Example ===")

    try:
        bot_user = await NotionBotUser.from_current_integration()

        if not bot_user:
            raise ValueError("No bot user found in the current integration")

        print("✅ Found bot user:")
        print(f"   Name: {bot_user.name}")
        print(f"   ID: {bot_user.id}")
        print(f"   Workspace: {bot_user.workspace_name}")
        print(f"   Owner Type: {bot_user.owner_type}")
        print(f"   Max Upload: {bot_user.max_file_upload_size / (1024*1024):.2f} MB")

    except ValueError as e:
        print(f"❌ No suitable bot user found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run the example"""
    await example_from_current_integration()


if __name__ == "__main__":
    asyncio.run(main())
