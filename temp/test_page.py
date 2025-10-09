from notionary import NotionPage

PAGE = "Jarvis Clipboard"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    # Create content with nested top-level blocks (toggles with children)
    markdown = """
+++ ## Project Overview
This is the main project overview with some details.
+++

+++ ## Meeting Notes
Notes from today's meeting.

- Follow up with team
- Schedule next meeting
+++

+++ ## Code Examples
Some code snippets for reference.

```python
def hello_world():
    print("Hello, World!")
```
+++

+++ ## Random Thoughts
Just some random thoughts and ideas.
+++

+++ ## Final Section
This is the final section with some content.
+++
    """

    print("Appending content with nested blocks...")
    await page.append_markdown(markdown)

    content = await page.get_markdown_content()
    print("Content after append:")
    print(content)
    print("\n" + "=" * 50 + "\n")

    print("Clearing page content...")
    await page.clear_page_content()

    content_after_clear = await page.get_markdown_content()
    print("Content after clear:")
    print(content_after_clear)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
