from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
```python
ist lit
```
[caption] Ist eine gute Sprache

::: columns
::: column
test
:::

::: column
fest nicht lit
:::

:::

::: callout
some new info

```python
hell = "world"
```
test
:::

    """
    content = await page.append_markdown(markdown)
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
