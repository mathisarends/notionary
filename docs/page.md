!!! info "Notion API Reference"
For the official Notion API reference on pages, see [developers.notion.com/reference/page](https://developers.notion.com/reference/page)

A `Page` in Notionary is a class for working with Notion pages. It allows you to read and modify both metadata (such as title, cover, and icons) and the actual page content. You can access properties, retrieve comments, and update the page content programmatically. All operations are available through async methods.

## Instantiating a Page

You can create a Page object in Notionary using several methods:

```python
from notionary import NotionPage

page = await NotionPage.from_id("your-page-id")
```

```python
from notionary import NotionPage

page = await NotionPage.from_title("My Project")
```

```python
from notionary import NotionPage

page = await NotionPage.from_url("https://www.notion.so/your-workspace/your-page-id")
```

Most likely you want to use the `from_title` method as it's the most human readable format.

## Setting Metadata

You can update a page's presentation and lifecycle metadata. Supported operations include:

- Set the title
- Set or remove an emoji icon
- Set or remove an external icon (image URL)
- Set, randomize, or remove the cover image
- Move the page to trash / restore it

### Examples

Set the title:

```python
await page.set_title("Weekly Planning")
```

Emoji icon:

```python
await page.set_emoji_icon("🗂️")
await page.remove_icon()  # removes emoji or external icon
```

External icon:

```python
await page.set_external_icon("https://example.com/icon.png")
```

Cover image:

```python
await page.set_cover_image_by_url("https://example.com/cover.png")
await page.set_random_gradient_cover()  # built‑in Notion gradient
await page.remove_cover_image()
```

Trash / restore:

```python
await page.move_to_trash()
await page.restore_from_trash()
```

All metadata setters are async and immediately update the in-memory object with the API response values.

## Working with Content

Notionary provides a flexible way to work with page content. You can:

- Retrieve the current content
- Append new content
- Prepend content
- Remove content blocks

### Examples

Retrieve content:

```python
content = await page.get_markdown_content()
print(content)
```

Append content:

```python
await page.append_markdown("## This is a new section")
```

Remove content:

```python
await page.clear_page_content()
```

## Comments

You can list existing comments on a page and create new ones.

List comments:

```python
comments = await page.get_comments()
for comment in comments:
    print(comment.rich_text)
```

Post a new CommentDto:

```python
await page.post_comment("This page will be reviewed tomorrow")
```
