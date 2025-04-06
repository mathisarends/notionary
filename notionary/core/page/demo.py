import asyncio
import json

from notionary.core.page.notion_page_manager import NotionPageManager

async def demo():
    """Demonstration der wichtigsten Funktionen der NotionPageManager-Fassade."""

    # Die zu bearbeitende Notion-Page
    page_id = "1c8389d5-7bd3-814a-974e-f9e706569b16"
    manager = NotionPageManager(page_id=page_id)

    try:
        print("🔧 Setze Titel ...")
        await manager.set_title("📘 Neue Testseite mit Bookmarks")

        print("🔧 Setze Icon ...")
        await manager.set_page_icon(emoji="🔖")

        print("🔧 Setze Cover ...")
        await manager.set_page_cover("https://source.unsplash.com/random/1200x300")

        print("🧩 Aktualisiere Property ...")
        await manager.update_property_by_name("Status", "Überarbeiten")

        print("📝 Ersetze Markdown-Inhalt ...")
        markdown = """# Beispiel mit Bookmarks

[bookmark](https://claude.ai/chat/a241fdb4-6526-4e0e-9a9f-c4573e7e834d "Erklärchat")

[bookmark](https://claude.ai/chat/534901ea-0592-4c9b-ad71-ade0a4260704 "Zweiter Bookmark")
"""
        await manager.replace_content(markdown)

        print("📄 Inhalt der Seite (als Text):")
        text = await manager.get_text()
        print(text)

        print("📦 Metadaten:")
        metadata = await manager.get_metadata()
        print(json.dumps(metadata, indent=2, ensure_ascii=False))

    finally:
        print("🧹 Schließe Client-Verbindung")
        await manager.close()


if __name__ == "__main__":
    asyncio.run(demo())