# Page

A `Page` object lets you manage a single Notion page — its metadata (title, icon, cover), content (via the Markdown API), properties, and comments.

## Finding Pages

Pages are accessed through the `notion.pages` namespace:

```python
from notionary import Notionary

async with Notionary() as notion:
    # By title (case-insensitive, raises PageNotFound with suggestions on miss)
    page = await notion.pages.from_title("Weekly Planning")

    # By UUID
    page = await notion.pages.from_id("your-page-id")

    # List / search
    pages = await notion.pages.list(query="roadmap")

    # Stream results (memory-efficient)
    async for page in notion.pages.iter(query="spec"):
        print(page.title)
```

## Metadata

```python
await page.rename("Sprint 42 Planning")

# Icon
await page.set_icon_emoji("🗂️")
await page.set_icon_url("https://example.com/icon.png")
await page.set_icon_from_file("./icon.png")
await page.remove_icon()

# Cover
await page.set_cover("https://example.com/cover.png")
await page.random_cover()          # built-in Notion gradient
await page.set_cover_from_file("./cover.png")
await page.remove_cover()

# Trash
await page.trash()
await page.restore()

# Lock / unlock
await page.lock()
await page.unlock()
```

## Content (Markdown API)

Page content is read and written as Markdown via the [Notion Markdown API](https://developers.notion.com/reference/retrieve-page-markdown).

```python
md = await page.get_markdown()

await page.append("## New Section\nSome text here.")

await page.replace("# Complete Rewrite\nFresh content.")

await page.clear()
```

## Properties

The `page.properties` object exposes a single generic setter:

```python
await page.properties.set_property("Status", "In Progress")
await page.properties.set_property("Effort", 5)
await page.properties.set_property("Tags", ["Backend", "API"])
await page.properties.set_property("Due", {"start": "2025-10-01"})
await page.properties.set_title("New Title")
```

The value is dispatched to the correct Notion property type automatically.

## Comments

```python
await page.comment("This page will be reviewed tomorrow.")
```

## Templates

```python
await page.apply_default_template(timezone="Europe/Berlin")
await page.apply_template(template_id, erase_content=True)
```

## Reference

!!! info "Notion API Reference" - [Pages](https://developers.notion.com/reference/page) - [Markdown API](https://developers.notion.com/reference/retrieve-page-markdown) - [Comments](https://developers.notion.com/reference/retrieve-a-comment)
