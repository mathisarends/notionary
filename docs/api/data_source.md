# Data Source

## DataSourceNamespace

Access data sources through `notion.data_sources`.

```python
async with Notionary() as notion:
    ds = await notion.data_sources.from_title("Engineering Backlog")
    all_ds = await notion.data_sources.list()
```

::: notionary.data_source.namespace.DataSourceNamespace

---

## DataSource

A single Notion data source with metadata, properties, and page creation.

```python
page = await ds.create_page(title="New Feature")
await ds.set_title("Sprint Board")
```

::: notionary.data_source.data_source.DataSource

!!! info "Notion API Reference"
[Data Sources](https://developers.notion.com/reference/data-source)
