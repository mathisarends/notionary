A `DataSource` represents a structured collection of rows (pages) inside a database. It exposes metadata (title, description, icon, cover, archive state) and typed property definitions. Pages created in or returned from a data source adopt these property schemas.

```mermaid
flowchart TD
    DB[Database]

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

## Instantiating a Data Source

```python
from notionary import NotionDataSource

data_source = await NotionDataSource.from_id("your-data-source-id")
```

```python
from notionary import NotionDataSource

data_source = await NotionDataSource.from_title("Features Backlog")
```

```python
from notionary import NotionDataSource

data_source = await NotionDataSource.from_url("https://www.notion.so/your-workspace/your-data-source-id")
```

`from_title` / `from_url` use the Notion search API to find the best match.

## Metadata Operations

```python
await data_source.set_title("Sprint Board")
await data_source.set_emoji_icon("🧭")
await data_source.set_external_icon("https://example.com/icon.png")
await data_source.set_cover_image_by_url("https://example.com/cover.png")
await data_source.set_random_gradient_cover()
await data_source.remove_cover_image()
await data_source.archive()
await data_source.unarchive()
await data_source.update_description("Contains all upcoming features.")
```

All operations are async and update the in‑memory fields after a successful API response.

## Property Options

Every data source lets you inspect allowed option values for properties. This is the authoritative place to discover what values downstream pages (rows) are allowed to use.

### Get all allowed option labels

Use this when you do not care about the concrete property category and just want the permissible labels.

```python
options = await data_source.get_options_for_property_by_name("Status")
print(options)  # e.g. ['Todo', 'In Progress', 'Done']
```

### Specific helpers per property kind

```python
select_options = data_source.get_select_options_by_property_name("Phase")

multi_select_options = data_source.get_multi_select_options_by_property_name("Labels")

status_options = data_source.get_status_options_by_property_name("Status")

relation_target_titles = await data_source.get_relation_options_by_property_name("Epic")
```

Notes:

- The helpers return plain strings (option names / relation target titles). These are exactly the human‑readable values that page‑level property writer methods expect when you later set a select / multi‑select / status / relation value on an individual page.
- An empty list means either the property does not exist, has no configured options yet, or (for relations) the related data source currently has no target pages.

### Relation option discovery

For relation properties the method fetches all current target page titles from the related data source. This allows you to pre‑validate user input and present an autocomplete for cross‑workspace linking. The titles you get here are what you pass later (on the page layer) to the relation‑setting helper which resolves them internally to page IDs.

```python
related_titles = await data_source.get_relation_options_by_property_name("Epic")
for title in related_titles:
    print("Possible related page:", title)
```

## Querying pages

The `NotionDataSource` exposes top-level query helpers to find pages (rows) that belong to a data source. You can build filters with the `DataSourceQueryBuilder` and run them synchronously (collecting results) or as an async stream.

### Using the builder directly

```python
builder = data_source.filter()
params = builder.where("Status").equals("In Progress").order_by_last_edited_time().build()

pages = await data_source.get_pages(query_params=params)
```

### Convenient helpers

`NotionDataSource` provides convenience helpers that accept a small builder function:

```python
pages = await data_source.query(lambda b: b.where("Status").equals("In Progress").order_by("Effort"))

async for page in data_source.query_stream(lambda b: b.where("Tags").array_contains("API")):
    print(page.title)

builder = data_source.filter()
params = builder.where("Phase").equals("Design").build()
pages = await data_source.get_pages(query_params=params)

all_pages = await data_source.get_pages()

async for p in data_source.get_pages_stream():
    print(p.title)
```

Stream methods (like `query_stream` and `get_pages_stream`) return an async generator that yields `NotionPage` objects as they are fetched from the API. This approach is memory-efficient because it does not load the entire result set into memory, and it works well for automated pipelines or streaming processing where you can consume pages one-by-one.

Notes:

- `filter()` returns a pre-seeded `DataSourceQueryBuilder` using the data source's property definitions.
- `query()` accepts a function that receives a builder and should return the configured builder; it resolves the params and returns a list of `NotionPage` objects.
- `query_stream()` works similarly but yields pages asynchronously as they are fetched.
- `get_pages()` and `get_pages_stream()` also accept an optional `query_params` object if you already built the params yourself.

## Reference

!!! info "Notion API Reference"
For the official Notion API reference on datasources, see [https://developers.notion.com/reference/data-source](https://developers.notion.com/reference/data-source)
