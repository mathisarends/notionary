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

## Tabelle mit Daten

| Name  | Alter | Beruf         |
| ----- | ----- | ------------- |
| Anna  | 29    | Designerin    |
| Ben   | 35    | Entwickler    |
| Clara | 41    | Projektleiterin |

## Weitere Sektion

!> [🚧] Dies ist ein Callout mit einem Hinweistext

---

## Noch ein Codeblock – JSON

```json
{
  "name": "Mathis",
  "projekte": ["Notion", "Automation"],
  "aktiv": true
}
```

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

Bla Bla

> Ein normales Blockzitat ohne spezielle Farbe.

"""
    
    await append_markdown(page_id=page_id, markdown_text=markdown)
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())