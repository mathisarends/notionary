"""
Creates an epic "Never Gonna Give You Up" themed page using MarkdownBuilder.
This demonstrates the full power of Notionary's markdown conversion capabilities!
"""

import asyncio

from notionary import MarkdownBuilder, NotionDataSource

DATA_SOURCE_TITLE = "Inbox"


async def main() -> None:
    data_source = await NotionDataSource.from_title(DATA_SOURCE_TITLE)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    page = await data_source.create_blank_page(title="Never Gonna Give You Up")

    await page.set_emoji_icon("🎶")
    await page.set_random_gradient_cover()

    markdown_content = (
        MarkdownBuilder()
        .video(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            caption="The official music video - Click if you dare! 🎬",
        )
        .h2("Fun Stats & Achievements")
        .todo_list(
            [
                "Over 1 billion views on YouTube",
                "Most rickrolled song of all time",
                "2009: Inducted into the Meme Hall of Fame",
                "2016: Rick Astley made an appearance at Macy's Thanksgiving Day Parade",
                "2020: Rickroll reached its peak during COVID-19 lockdowns",
            ],
            completed=[True, True, True, True, True],
        )
        .space()
        .paragraph("*This page was created with Notionary's MarkdownBuilder*")
        .build()
    )

    print("Appending markdown to page...")
    await page.append_markdown(markdown_content)

    print(f"✨ Created epic meme page at: {page.url}")
    print("🎵 Never gonna let you down!")


if __name__ == "__main__":
    asyncio.run(main())
