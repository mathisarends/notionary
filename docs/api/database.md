# Database

## DatabaseNamespace

Access databases through `notion.databases`.

```python
async with Notionary() as notion:
    db = await notion.databases.from_title("Tasks")
    db = await notion.databases.create(title="New DB", icon_emoji="📊")
```

::: notionary.database.namespace.DatabaseNamespace

---

## Database

A single Notion database with metadata, icon, cover, and lock state.

```python
await db.set_title("Project Tracker")
await db.set_description("All current projects")
await db.lock()
```

::: notionary.database.database.Database

!!! info "Notion API Reference"
[Databases](https://developers.notion.com/reference/database)
