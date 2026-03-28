# Page

## PageNamespace

Access pages through `notion.pages`.

```python
async with Notionary() as notion:
    page = await notion.pages.from_title("Meeting Notes")
    pages = await notion.pages.list(query="roadmap")
```

::: notionary.page.namespace.PageNamespace

---

## Page

A single Notion page with content, properties, comments, and metadata.

Content operations use the [Notion Markdown API](https://developers.notion.com/reference/retrieve-page-markdown) –
Notionary delegates directly to it.

```python
md = await page.get_markdown()
await page.append("## New Section")
await page.replace("# Replaced")
await page.clear()
```

::: notionary.page.page.Page

---

## PageProperties

::: notionary.page.properties.service.PageProperties

---

## PageComments

::: notionary.page.comments.service.PageComments

---

## Comment

::: notionary.page.comments.models.Comment

!!! info "Notion API Reference"
[Pages](https://developers.notion.com/reference/page) ·
[Markdown](https://developers.notion.com/reference/retrieve-page-markdown) ·
[Comments](https://developers.notion.com/reference/retrieve-a-comment)
