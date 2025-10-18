import asyncio

from notionary import NotionPage
from notionary.comments import Comment

# Replace with title of your page
PAGE_TITLE = "Neue super page"


async def main() -> None:
    page = await NotionPage.from_title(PAGE_TITLE)
    print(f"Found page: {page.title} (URL: {page.url})")

    comments = await page.get_comments()
    _print_comments(comments)

    print("\nAdding a new comment...")
    await page.post_top_level_comment("This is a new comment from Notionary!")
    await page.post_top_level_comment("It even suppors markdown! **Bold** _Italic_")

    print("Look at the page at ", page.url, "to see your comments added.")


def _print_comments(comments: list[Comment]) -> None:
    if not comments:
        print("No comments found.")

    for comment in comments:
        print(f"- {comment.content} (by {comment.author_name})")


if __name__ == "__main__":
    asyncio.run(main())
