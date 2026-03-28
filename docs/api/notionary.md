# Notionary

The main entry point for the library. Create a `Notionary` instance to access all Notion API namespaces.

```python
from notionary import Notionary

async with Notionary() as notion:
    page = await notion.pages.from_title("My Page")
```

::: notionary.service.Notionary

!!! info "Notion API Reference"
[developers.notion.com](https://developers.notion.com/)
