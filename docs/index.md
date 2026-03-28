# Notionary

Transform complex Notion API interactions into simple, Pythonic code. Whether you're building AI agents, automating workflows, or creating dynamic content, Notionary makes it effortless.

## Why use Notionary?

- **Object-Oriented Wrapper** – Clean Python classes for pages, databases, data sources, and file uploads instead of raw JSON.
- **Smart Discovery** – Find pages and databases by title with fuzzy matching. No UUIDs needed.
- **Markdown Content** – Read and write page content as Markdown via the [Notion Markdown API](https://developers.notion.com/reference/retrieve-page-markdown).
- **Async-First** – Modern Python with full `async`/`await` support.
- **Type Safety** – Pydantic models and type hints throughout.

## Installation

```bash
pip install notionary
```

## Hello World

```python
import asyncio
from notionary import Notionary

async def main():
    async with Notionary() as notion:
        page = await notion.pages.from_title("My Project")
        md = await page.get_markdown()
        print(md)

        await page.append("## Updated by Notionary!")

asyncio.run(main())
```

Set the `NOTION_API_KEY` environment variable before running:

```bash
export NOTION_API_KEY=ntn_...
```
