"""
# Notionary: Batch Processing Test
===============================

This example demonstrates how to append large amounts of markdown content
to a Notion page, testing the batch processing functionality that handles
the Notion API's 100-block limit per request.

IMPORTANT: Replace "Jarvis Clipboard" with the actual name of your page.
"""

import asyncio
import random
import time
import traceback

from notionary import NotionPage

YOUR_PAGE_NAME = "Jarvis Clipboard"


async def generate_many_blocks(num_blocks=250):
    """
    Generate a markdown string with many blocks to test batch processing.

    Args:
        num_blocks: Number of blocks to generate (default: 250)

    Returns:
        A markdown string with many blocks
    """
    block_types = [
        "heading",
        "paragraph",
        "code",
        "bulleted_list",
        "numbered_list",
        "quote",
        "callout",
        "toggle",
    ]

    markdown = "# Batch Processing Test\n\n"
    markdown += f"Testing appending {num_blocks} blocks to a Notion page\n\n"

    for i in range(num_blocks):
        block_type = random.choice(block_types)

        if block_type == "heading":
            level = random.randint(1, 3)
            markdown += f"{'#' * level} Block {i}: Heading {level}\n\n"

        elif block_type == "paragraph":
            markdown += f"This is paragraph block {i}. Testing the batch processing functionality.\n\n"

        elif block_type == "code":
            lang = random.choice(["python", "javascript", "bash"])
            markdown += f"```{lang}\n# Block {i}: Code sample\nprint('Testing batch processing')\n```\n\n"

        elif block_type == "bulleted_list":
            markdown += (
                f"- Bullet point {i}.1\n- Bullet point {i}.2\n- Bullet point {i}.3\n\n"
            )

        elif block_type == "numbered_list":
            markdown += f"1. Numbered item {i}.1\n2. Numbered item {i}.2\n3. Numbered item {i}.3\n\n"

        elif block_type == "quote":
            markdown += f"> This is a quote in block {i}. Testing batch processing.\n\n"

        elif block_type == "callout":
            emoji = random.choice(["💡", "⚠️", "💻", "🔍", "📊"])
            markdown += f"!> [{emoji}] Callout block {i}\n| This is a callout to test batch processing.\n\n"

        elif block_type == "toggle":
            markdown += f"+++ Toggle block {i}\n| Hidden content for testing batch processing.\n\n"

    return markdown


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""
    try:
        print("Searching for page by name...")
        page = await NotionPage.from_title(YOUR_PAGE_NAME)

        print(f'✅ Found: "{page.title}" {page.emoji_icon} → {page.url}')

        # Generate a large number of blocks
        num_blocks = 250  # This should trigger at least 3 batches (100, 100, 50)
        print(f"Generating {num_blocks} blocks...")
        markdown_content = await generate_many_blocks(num_blocks)

        # Time the operation to see batch processing in action
        start_time = time.time()

        print(
            f"Appending {num_blocks} blocks to the page (will be processed in batches of 100)..."
        )
        result = await page.append_markdown(markdown_content, append_divider=True)

        end_time = time.time()
        duration = end_time - start_time

        print(f"✅ Markdown appended: {result}")
        print(f"⏱️ Operation took {duration:.2f} seconds")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    print("🚀 Starting Notionary Batch Processing Test...")
    asyncio.run(main())
