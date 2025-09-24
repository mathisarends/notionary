# NotionPage Markdown I/O — Guide

Use `NotionPage.append_markdown(...)` and `replace_content(...)` to write **Notionary Markdown** to a page. Content can be provided either as a **raw markdown string** or via a **builder callback** that receives a `MarkdownBuilder`. Conversions are **round‑trip capable**: you can read page content back as Notionary Markdown and re‑apply it later.

---

## Two Ways to Provide Content

### 1) Raw Notionary Markdown (quick & manual)

```python
from notionary import NotionPage

content = """
# Hello

This content was written as raw Notionary Markdown.
- Bullet A
- Bullet B
"""

page = await NotionPage.from_title("Docs Playground")
await page.append_markdown(content)
```

### 2) Builder Callback (recommended)

Pass a function that **receives a `MarkdownBuilder`** and returns it after configuring. This avoids typos and keeps structure explicit.

```python
from notionary import NotionPage, MarkdownBuilder

async def write_with_builder():
    page = await NotionPage.from_title("Docs Playground")

    await page.append_markdown(
        lambda b: (b
            .h1("Quick Start")
            .paragraph("Built via MarkdownBuilder callback.")
            .bulleted_list(["Type‑safe mapping", "Clean structure"])
            .divider()
            .h2("Next")
            .numbered_list(["Install", "Configure", "Deploy"])
        ),
        prepend_table_of_contents=True,
        append_divider=True,
    )
```

> The page methods **create** a `MarkdownBuilder` and hand it to your callback. Return the same builder (after chaining) or **return a new one** if you prefer full control (see below).

---

## Dependency Injection Patterns

### A) Use the provided builder (typical)

```python
def section(builder: MarkdownBuilder) -> MarkdownBuilder:
    return (builder
        .h2("Section")
        .paragraph("Uses the provided builder instance.")
    )

await page.append_markdown(section)
```

### B) Return your own preconfigured builder (advanced)

```python
def provide_custom_builder(_: MarkdownBuilder) -> MarkdownBuilder:
    # ignore the provided instance, return your own
    custom = MarkdownBuilder().h2("Custom").paragraph("Own instance returned.")
    return custom

await page.append_markdown(provide_custom_builder)
```

Both patterns are valid because the signature is:

```python
content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder]]
```

---

## Round‑Trip Conversion

`get_text_content()` returns the page as **Notionary Markdown**. You can modify it or re‑apply it, enabling round‑trip workflows.

```python
page = await NotionPage.from_title("Docs Playground")
original_md = await page.get_text_content()

# ... edit original_md or store it ...

await page.replace_content(original_md, prepend_table_of_contents=False)
```

---

## API Reference (concise)

### `append_markdown(...) -> bool`

```python
async def append_markdown(
    content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder]],
    *,
    prepend_table_of_contents: bool = False,
    append_divider: bool = False,
) -> bool
```

- **content**: raw Notionary Markdown **or** a callback that receives a `MarkdownBuilder` and returns it.
- **prepend_table_of_contents**: add a table of contents before your content.
- **append_divider**: add a divider after your content.

### `replace_content(...) -> bool`

Same signature and options as `append_markdown`, but clears the page first:

```python
await page.replace_content(lambda b: b.h1("Fresh Start").paragraph("…"))
```

### `get_text_content() -> str`

Returns the page converted **back** to Notionary Markdown for storage, editing, or re‑rendering.

---

## Minimal End‑to‑End Example

```python
from notionary import NotionPage, MarkdownBuilder

async def demo():
    page = await NotionPage.from_title("Builder Demo")

    # Write via builder
    await page.replace_content(lambda b: (b
        .h1("Builder Demo")
        .paragraph("Generated with a fluent API.")
        .bulleted_list(["Safe mapping", "Readable code", "No typos"])
    ))

    # Read back (round‑trip)
    md = await page.get_text_content()

    # Append an extra section using raw markdown
    await page.append_markdown(md + "\n\n## Changelog\n- Added demo section\n")
```

---

## Notes

- These methods are **always used in the context of a `NotionPage`** instance.
- The builder maps **1:1 to block nodes**; the markdown string produced by `.build()` is what the page writer consumes.
- Prefer the builder for programmatic generation and consistency across pages.
