A `Database` in Notionary is a container object that stores structure and presentation metadata (title, description, icon, cover, inline state) and provides access to its data sources. Since API version `2025-09-03`, a database no longer directly stores the row data; instead, each data source attached to it holds the actual pages (rows), and the database acts as an umbrella for those sources.

```mermaid
flowchart TD
    DB[(Database)]

    DS1[(Data Source)]
    DS2[(Data Source)]

    P1[Page]
    P2[Page]
    P3[Page]
    P4[Page]

    DB --> DS1
    DB --> DS2

    DS1 --> P1
    DS1 --> P2
    DS2 --> P3
    DS2 --> P4
```

## Instantiating a Database

You can create a `Database` object using:

```python
from notionary import NotionDatabase

db = await NotionDatabase.from_id("your-database-id")
```

```python
from notionary import NotionDatabase

db = await NotionDatabase.from_title("Tasks")
```

```python
from notionary import NotionDatabase

db = await NotionDatabase.from_url("https://www.notion.so/your-workspace/your-database-id")
```

Most likely you want to use `from_title` when working interactively.

## Setting Metadata

You can update database‑level metadata similar to pages:

- Set title
- Set or remove emoji icon
- Set or remove external icon
- Set, randomize, or remove cover image
- Move to trash / restore

### Examples

p

```python
await db.set_title("Project Tracker")
await db.set_emoji_icon("📊")
await db.set_external_icon("https://example.com/icon.png")
await db.set_cover_image_by_url("https://example.com/cover.png")
await db.set_random_gradient_cover()
await db.remove_cover_image()
await db.move_to_trash()
await db.restore_from_trash()
```

## Working with Data Sources

A database lazily loads its underlying data sources. The first call to `get_data_sources()` triggers a fetch; subsequent calls return the cached list.

```python
data_sources = await db.get_data_sources()
for data_source in data_sources:
    print(data_source.title, data_source.id)
```

Each data source exposes its own properties and can yield pages / rows through its querying interface (see the Data Source documentation for details).

## Reference

!!! info "Notion API Reference"
For the official Notion API reference on databases, see [https://developers.notion.com/reference/database](https://developers.notion.com/reference/database)
