import os
import asyncio

from notionary.blocks.rich_text.name_to_id_resolver import NameIdResolver

async def main():
    # Initialize resolver with your Notion integration token
    resolver = NameIdResolver()

    # Test data
    page_id = "1a3389d57bd380d7a507e67d1b25822c"
    page_name = "Jarvis Clipboard"

    # Resolve name -> ID
    resolved_id = await resolver.resolve_id(page_name)
    print(f"Resolved ID for name '{page_name}': {resolved_id}")

    # Resolve ID -> name
    resolved_name = await resolver.resolve_name(page_id)
    print(f"Resolved name for ID '{page_id}': {resolved_name}")

if __name__ == "__main__":
    asyncio.run(main())
