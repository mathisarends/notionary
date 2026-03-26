import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.from_title("Eleven Labs")

        await page.append("""
## Test der Enhanced Markdown API

<callout icon="🔥" color="red_bg">
	Das ist ein **Callout** mit rotem Hintergrund und `inline code`
</callout>

<callout icon="💡" color="blue_bg">
	Und noch einer in *blau* – mit ~~durchgestrichen~~ und <span underline="true">unterstrichen</span>
</callout>

<details>
<summary>Toggle Block</summary>
	Hier ist der versteckte Inhalt
	Noch eine Zeile
</details>

# Heading 1 {color="blue"}
## Heading 2 {color="red"}
### Heading 3 {color="green"}

- [ ] Unchecked Todo
- [x] Checked Todo
- Bulleted item mit **fett** und *kursiv*
	- Nested item
		- Doppelt nested

1. Erstes Element
2. Zweites Element

> Line 1<br>Line 2<br>Line 3 {color="purple"}

---

<columns>
	<column>
		Linke Spalte mit **fett**
	</column>
	<column>
		Rechte Spalte mit *kursiv*
	</column>
</columns>

<table header-row="true">
	<tr>
		<td>Name</td>
		<td>Status</td>
		<td>Priorität</td>
	</tr>
	<tr>
		<td>Feature A</td>
		<td>Done</td>
		<td>High</td>
	</tr>
</table>
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

$$
E = mc^2
$$

<table_of_contents/>
""")
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
