# Workspace

Access workspace-wide search through `notion.workspace`.

```python
async with Notionary() as notion:
    results = await notion.workspace.search(query="roadmap")
```

::: notionary.workspace.namespace.WorkspaceNamespace

!!! info "Notion API Reference"
[Search](https://developers.notion.com/reference/post-search)
