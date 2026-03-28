# Workspace

The `workspace` namespace provides cross-resource search across your entire Notion workspace. It returns a mixed list of `Page` and `DataSource` objects.

## Searching

```python
from notionary import Notionary

async with Notionary() as notion:
    results = await notion.workspace.search(query="roadmap")

    for item in results:
        print(type(item).__name__, item.title)
```

Results include both pages and data sources. Use `isinstance()` to distinguish them if needed.

## Reference

!!! info "Notion API Reference"
[Search](https://developers.notion.com/reference/post-search)
