# File Upload Integration

How uploaded files connect to pages, data sources, databases and blocks.

Related docs: [Pages](../page.md) · [Database](../database.md) · [Resolver](resolver.md)

## Page assets (icon & cover)

```python
from notionary import NotionPage

page = await NotionPage.from_id("your-page-id")

# Set icon from existing upload id
await page.set_icon_from_file_upload(response.id)

# Set cover image from existing upload id
await page.set_cover_image_from_file_upload(response.id)

# Direct upload from disk + apply
await page.set_icon_from_file(Path("./assets/icon.png"))
await page.set_cover_image_from_file(Path("./assets/cover.jpg"))

# From bytes
await page.set_icon_from_bytes(icon_bytes, filename="spark.png")
await page.set_cover_image_from_bytes(cover_bytes, filename="gradient.png")
```

## Data source / database metadata

Pattern mirrors pages; you can set cover or icon where supported.

```python
from notionary import NotionDataSource

ds = await NotionDataSource.from_id("data-source-id")
await ds.set_cover_image_from_file_upload(response.id)
```
