import textwrap
from notionary.converters import MarkdownToNotionConverter
from notionary.core.notion_client import NotionClient

async def append_markdown(page_id: str, markdown_text: str) -> str:
    notion_client = NotionClient()
    notion_markdown_converter = MarkdownToNotionConverter()
    content_blocks = notion_markdown_converter.convert(markdown_text=markdown_text)
        
    data = {
        "children": content_blocks
    }
        
    result = await notion_client.patch(f"blocks/{page_id}/children", data)
        
    if result:
        print("Successfully added text to the page.")

async def demo():
    """Example usage of the NotionContentManager."""
    page_id = "1a3389d5-7bd3-80d7-a507-e67d1b25822c"
    
    markdown = """# Beispiel mit Codeblöcken und Tabellen

Hier ist ein Codeblock in Python:

```python
def greet(name):
    return f"Hallo, {name}!"

print(greet("Mathis"))
```
<!-- spacer -->

## Tabelle mit Daten

| Name  | Alter | Beruf         |
| ----- | ----- | ------------- |
| Anna  | 29    | Designerin    |
| Ben   | 35    | Entwickler    |
| Clara | 41    | Projektleiterin |

## Weitere Sektion

!> [🚧] Dies ist ein Callout mit einem Hinweistext

---

## Video Embed Beispiel

Hier ist ein eingebettetes Video von YouTube:

@[Einführung in Python-Programmierung](https://www.youtube.com/watch?v=rfscVS0vtbw)

Und ein weiteres Video ohne Beschriftung:

@[](https://vimeo.com/148751763)

---

## Noch ein Codeblock – JSON

```json
{
"name": "Mathis",
"projekte": ["Notion", "Automation"],
"aktiv": true
}
```
<!-- spacer -->
<!-- spacer -->

## Toggle Inhalt

Auch hier ist etwas Inhalt in einem Toggle versteckt.

```bash
echo "Toggle mit Codeblock"
```

## Aufgabenliste

- [ ] Implementierung des TodoElement abschließen
- [x] Markdown-Parser überprüfen
- [ ] Tabellen-Element testen
- [ ] Code-Block-Formatierung optimieren
- [x] Callout-Elemente unterstützen
- [ ] Dokumentation aktualisieren
- [ ] Unit-Tests für alle Element-Typen schreiben
- [x] Element-Registry implementieren
- [ ] Integration mit Notion API testen
- [ ] Regressionstests durchführen

## Formatierungsbeispiele

Hier folgen einige **Formatierungsbeispiele** zum Testen:

1. **Fettgedruckter** Text mit `Code-Snippet` darin
2. *Kursiver* Text mit __unterstrichenem__ Abschnitt
3. ~~Durchgestrichener~~ Text mit **_gemischter Formatierung_**
4. Hervorhebungen in ==yellow:Gelb== und ==blue:Blau==
5. Ein [Link mit **Formatierung**](https://notion.so) darin
6. Verschachtelte `Formatierungen` mit *`gemischten`* **Stilen**
7. Text mit ==red_background:farbigem Hintergrund==

## Farbige Blockzitate

> [background:brown] Dies ist ein Blockzitat mit braunem Hintergrund.
> Es kann mehrere Zeilen enthalten.

Bla Bla

> [color:yellow] Und hier ist ein gelbes Blockzitat.
> Mit mehreren Absätzen.
<!-- spacer -->

Bla Bla

[bookmark](https://claude.ai/chat/a241fdb4-6526-4e0e-9a9f-c4573e7e834d "Beispieltitel")

## Bilder und Videos

Hier ist ein Bild mit Beschriftung:
![Ein schönes Landschaftsbild](https://images.unsplash.com/photo-1506744038136-46273834b3fb)

Und hier noch ein direkt eingebettetes Video:
@[Ein Naturdokumentarfilm](https://example.com/naturvideo.mp4)
"""

    markdown_yt = """# YouTube Video Embeds in Columns
::: columns
::: column
## Standard YouTube URL
@[Learn Python - Full Course for Beginners](https://www.youtube.com/watch?v=rfscVS0vtbw)
:::
::: column
## YouTube Shortened URL
@[Python Tutorial](https://youtu.be/Z1Yd7upQsXY)
:::
::: column
## YouTube URL without Caption
@[](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
:::
:::

## Toggle Section Below

+++ Toggle title
    Indented content that belongs to the toggle
    More indented content

+++ Empty Toggle

## Videos With Toggles in Columns

::: columns
::: column
### Video with Toggle
@[Python Tips](https://www.youtube.com/watch?v=C-gEQdGVXbk)

+++ Toggle Details
    This video contains good Python tips
    for beginners and advanced users
:::
::: column
### Another Video with Toggle
@[Data Science](https://youtu.be/ua-CiDNNj30)

+++ Video Description
    Learn about data science
    and pandas library in Python
:::
:::
"""
    
    await append_markdown(page_id=page_id, markdown_text=markdown_yt)
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())