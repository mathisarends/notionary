A `Page` in Notionary is a class for working with Notion pages. It allows you to read and modify both metadata (such as title, cover, and icons) and the actual page content. You can access properties, retrieve comments, and update the page content programmatically.

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

Replace content:

```python
await page.replace_content("This is some new content")
```

## Working with Comments

You can list existing comments on a page and create new ones.

List comments:

```python
comments = await page.get_comments()
for comment in comments:
    print(comment.author_name)
    print(comment.content)
```

Post a new CommentDto:

```python
await page.post_comment("This page will be reviewed tomorrow")
```

## Reading properties and discovering options

Note: the current API exposes a helper object `page.properties` for reading and writing page properties. Older examples used `page.property_reader` / `page.property_writer` — this has been simplified.

`page.properties` provides synchronous reader methods and asynchronous writer methods (the writers are `async`). If the page belongs to a DataSource, `page.properties` can also load valid options from that DataSource (for select/status/relation properties).

### Reading current values

Examples for reading property values (space between lines for readability):

```python
status = page.properties.get_value_of_status_property("Status")

labels = page.properties.get_values_of_multiselect_property("Tags")

url = page.properties.get_value_of_url_property("Repository")

number = page.properties.get_value_of_number_property("Effort")

description = await page.properties.get_value_of_rich_text_property("Description")
```

All reader methods return plain Python types (strings, floats, lists). Rich text fields are returned as Markdown strings.

### Discovering allowed option names from the DataSource

If the page belongs to a DataSource, you can query the allowed option labels from the DataSource (useful for validation or autocomplete):

```python
select_options = page.properties.get_select_options_by_property_name("Phase")

status_options = page.properties.get_status_options_by_property_name("Status")

labels_options = page.properties.get_multi_select_options_by_property_name("Tags")

relation_titles = await page.properties.get_relation_options_by_property_name("Epic")
```

These methods return readable strings (e.g. "Design", "In Progress") — exactly the values you should use when calling the `page.properties.set_*` writers.

## Setting properties

Property writes are intentionally explicit — there is no automatic type inference. Use the dedicated asynchronous setters on `page.properties` (the writers are `async`).

```python
await page.properties.set_rich_text_property("Description", "Refined spec")

await page.properties.set_url_property("Repository", "https://github.com/org/repo")

await page.properties.set_number_property("Effort", 5)

await page.properties.set_checkbox_property("Approved", True)

await page.properties.set_select_property_by_option_name("Phase", "Design")

await page.properties.set_multi_select_property_by_option_names("Tags", ["Backend", "API"])

await page.properties.set_status_property_by_option_name("Status", "In Progress")

await page.properties.set_date_property("Due", {"start": "2025-10-01"})
```

These setters expect human-readable values (for example, select labels). If the page belongs to a DataSource, the backend validates the supplied values against the allowed options from that DataSource.

### Relations

For relation properties you provide page titles; the API resolves those titles to the corresponding page IDs:

```python
await page.properties.set_relation_property_by_page_titles(
    "Epic",
    ["Platform Revamp", "Search Overhaul"],
)
```

Briefly, what happens under the hood:

1. The possible relation targets / options are queried from the associated DataSource if needed.
2. Titles are resolved to Page objects (pages are loaded by title).
3. The IDs of those pages are sent in the PATCH request to Notion.
4. After a successful patch the in-memory object (`page.properties`) is updated with the values returned by the API.

## Reference

!!! info "Notion API Reference"
For the official Notion API reference on pages, see [developers.notion.com/reference/page](https://developers.notion.com/reference/page)
