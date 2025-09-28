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

## Accessing Properties

A page exposes two coordinated helpers:

- `page.property_reader` – read current property values on the page (rich text, status, select, multi-select, numbers, etc.)
- `page.property_reader.data_source_reader` – (if the page belongs to a data source) access the data source level configuration to discover valid option labels for select / multi‑select / status / relation properties.

Under the hood the page keeps a reference to its parent data source (if any). That reference is what drives option validation and relation resolution when you write properties.

### Reading current values

```python
status = page.property_reader.get_value_of_status_property("Status")
labels = page.property_reader.get_values_of_multiselect_property("Tags")
url = page.property_reader.get_value_of_url_property("Repository")
number = page.property_reader.get_value_of_number_property("Effort")
rich_text = await page.property_reader.get_value_of_rich_text_property("Description")
```

### Discovering allowed option names (from the data source)

```python
select_options = page.property_reader.get_select_options_by_property_name("Phase")
status_options = page.property_reader.get_status_options_by_property_name("Status")
labels_options = page.property_reader.get_multi_select_options_by_property_name("Tags")
relation_titles = await page.property_reader.get_relation_options_by_property_name("Epic")
```

These methods return plain human‑readable strings – exactly what the writer methods expect when setting values.

## Setting Properties

Property writing is intentionally explicit – there is no generic "guess the type" method. Each property type has a dedicated async setter on `page.property_writer`:

```python
await page.property_writer.set_rich_text_property("Description", "Refined spec")
await page.property_writer.set_url_property("Repository", "https://github.com/org/repo")
await page.property_writer.set_number_property("Effort", 5)
await page.property_writer.set_checkbox_property("Approved", True)
await page.property_writer.set_select_property_by_option_name("Phase", "Design")
await page.property_writer.set_multi_select_property_by_option_names("Tags", ["Backend", "API"])
await page.property_writer.set_status_property_by_option_name("Status", "In Progress")
await page.property_writer.set_date_property("Due", {"start": "2025-10-01"})
```

### Relations

For relation properties you pass page titles. The writer resolves those titles to page IDs by consulting the related data source:

```python
await page.property_writer.set_relation_property_by_page_titles(
    "Epic",
    ["Platform Revamp", "Search Overhaul"],
)
```

Internally:

1. Option discovery happens via the parent data source's `property_reader` (relation target titles)
2. Titles -> Page objects (resolved by loading pages by title)
3. Page IDs are sent in the PATCH request
4. The in‑memory page properties are updated with the response

## Reference

!!! info "Notion API Reference"
For the official Notion API reference on pages, see [developers.notion.com/reference/page](https://developers.notion.com/reference/page)
