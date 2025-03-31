from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient, HttpMethod
from notionary.core.notion_content_converter import NotionContentConverter
from notionary.util.logging_mixin import LoggingMixin


class NotionPageManager(NotionClient, LoggingMixin):
    """Generische Klasse zum Schreiben und Verwalten von Notion-Seiten."""
    
    def __init__(self, page_id: str, token: Optional[str] = None):
        """Initialisiert den NotionPageWriter.
        
        Args:
            page_id: ID der Notion-Seite (direkt)
            page_name: Name der Notion-Seite (wird über NotionPages aufgelöst)
            token: Notion API Token
        """
        super().__init__(token=token)
        
        self.page_id = page_id
    
    async def get_page_content(self) -> List[Dict[str, Any]]:
        response = await self._make_request(
            HttpMethod.GET,
            f"blocks/{self.page_id}/children"
        )
        
        if "error" in response:
            self.logger.error("Fehler beim Abrufen des Seiteninhalts: %s", response.get('error'))
            return []
        
        return response.get("results", [])
    
    async def get_page_text(self) -> str:
        """Ruft den Seiteninhalt ab und konvertiert ihn in lesbaren Text.
        
        Returns:
            Textdarstellung des Seiteninhalts oder Fehlermeldung
        """
        blocks = await self.get_page_content()
        return NotionContentConverter.blocks_to_text(blocks)
    
    async def clear_page(self) -> str:
        blocks = await self.get_page_content()
        
        if not blocks:
            return "Keine Inhalte zum Löschen vorhanden oder Fehler beim Abrufen des Inhalts."
        
        # Jeden Block einzeln löschen
        deleted_count = 0
        for block in blocks:
            block_id = block.get("id")
            if not block_id:
                continue
                
            response = await self._make_request(
                HttpMethod.DELETE,
                f"blocks/{block_id}"
            )
            
            if "error" not in response:
                deleted_count += 1
        
        if deleted_count == len(blocks):
            self.logger.info("Alle %d Blöcke erfolgreich von der Seite gelöscht.", deleted_count)
            return f"Alle {deleted_count} Blöcke erfolgreich von der Seite gelöscht."
        else:
            self.logger.warning("Seite teilweise geleert. %d von %d Blöcken gelöscht.", deleted_count, len(blocks))
            return f"Seite teilweise geleert. {deleted_count} von {len(blocks)} Blöcken gelöscht."
    
    async def update_page_content(self, new_title: str = None, new_content: str = None, icon_emoji: str = "🤖") -> str:
        """Aktualisiert den Inhalt einer Notion-Seite inkl. Titel, Inhalt, Status und Icon.
        
        Args:
            new_title: Neuer Titel für die Seite (optional)
            new_content: Neuer Inhalt als Markdown-Text (optional)
            icon_emoji: Emoji-Icon für die Seite (Standard: Roboter-Emoji)
            
        Returns:
            Statusmeldung über den Erfolg der Aktualisierung
        """
        results = []
        
        # Titel und Icon in einem Request aktualisieren
        update_data = {
            "properties": {},
            "icon": {
                "type": "emoji",
                "emoji": icon_emoji
            }
        }
        
        # Titel hinzufügen, falls angegeben
        if new_title:
            update_data["properties"]["Name"] = {
                "title": [
                    {
                        "text": {
                            "content": new_title
                        }
                    }
                ]
            }
        
        # Status auf "KI-Draft" setzen
        update_data["properties"]["Status"] = {
            "status": {
                "name": "KI-Draft"
            }
        }
        
        # Page aktualisieren (Titel, Icon und Status in einem Request)
        update_response = await self._make_request(
            HttpMethod.PATCH,
            f"pages/{self.page_id}",
            update_data
        )
        
        if "error" in update_response:
            error_msg = f"Fehler bei der Aktualisierung der Seite: {update_response.get('error')}"
            self.logger.error(error_msg)
            results.append(error_msg)
        else:
            if new_title:
                self.logger.info("Titel erfolgreich aktualisiert: %s", new_title)
                results.append(f"Titel erfolgreich aktualisiert: {new_title}")
                # Attribute aktualisieren falls vorhanden
                if hasattr(self, 'title'):
                    self.title = new_title
                    
            self.logger.info("Icon erfolgreich auf %s gesetzt.", icon_emoji)
            results.append(f"Icon erfolgreich auf {icon_emoji} gesetzt.")
            
            self.logger.info("Status erfolgreich auf 'KI-Draft' gesetzt.")
            results.append("Status erfolgreich auf 'KI-Draft' gesetzt.")
        
        # Inhalt aktualisieren, falls angegeben
        if new_content:
            clear_result = await self.clear_page()
            results.append(clear_result)
            
            append_result = await self.append_content(new_content)
            results.append(append_result)
        
        return "\n".join(results)

    def extract_notion_metadata(self, page_content):
        """
        Dynamically extracts metadata from a Notion page content.
        """
        metadata = {}
        lines = page_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that appear to be metadata (key-value pairs)
            # Notion often formats metadata with icons/emojis or specific patterns
            
            # Check for common metadata patterns:
            # 1. Lines with a colon separating key and value
            if ':' in line and len(line.split(':', 1)) == 2:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
                continue
                
            # 2. Lines that have a clear visual separator between key and value
            for separator in ['  ', '   ', '\t']:
                if separator in line:
                    parts = line.split(separator, 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        metadata[parts[0].strip()] = parts[1].strip()
                        break
        
        # Clean up metadata - remove any entries that are likely not metadata
        # (e.g., too long to be a field name, or common page content)
        keys_to_remove = []
        for key in metadata:
            if len(key) > 30 or key.lower() in ['page', 'content', 'text']:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            metadata.pop(key)
        
        return metadata


    def get_metadata_by_key(self, page_content, key=None):
        """
        Gets all metadata or a specific metadata value by key.
        """
        metadata = self.extract_notion_metadata(page_content)
        
        if key:
            # Try exact match first
            if key in metadata:
                return metadata[key]
            
            # Try case-insensitive match
            for k in metadata:
                if k.lower() == key.lower():
                    return metadata[k]
            
            # Try partial match
            for k in metadata:
                if key.lower() in k.lower() or k.lower() in key.lower():
                    return metadata[k]
            
            return None
        
        return metadata
    
    async def get_page_metadata(self) -> Dict[str, Any]:
        """
        Extracts metadata from a Notion page properties.
        """
        # First, get the page itself to access its properties
        response = await self._make_request(
            HttpMethod.GET,
            f"pages/{self.page_id}"
        )
        
        if "error" in response:
            self.logger.error("Fehler beim Abrufen der Seiten-Metadaten: %s", response.get('error'))
            return {}
        
        metadata = {}
        
        # Extract properties from the response
        properties = response.get("properties", {})
        
        # Process different property types
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                # Extract title from title property
                rich_text = prop_data.get("title", [])
                title_parts = [text.get("plain_text", "") for text in rich_text]
                metadata[prop_name] = "".join(title_parts)
            
            elif prop_type == "rich_text":
                # Extract text from rich_text property
                rich_text = prop_data.get("rich_text", [])
                text_parts = [text.get("plain_text", "") for text in rich_text]
                metadata[prop_name] = "".join(text_parts)
            
            elif prop_type == "date":
                # Extract date information
                date_info = prop_data.get("date", {})
                if date_info:
                    start = date_info.get("start")
                    end = date_info.get("end")
                    if end:
                        metadata[prop_name] = f"{start} to {end}"
                    else:
                        metadata[prop_name] = start
            
            elif prop_type == "select":
                # Extract selected option
                select_info = prop_data.get("select", {})
                if select_info:
                    metadata[prop_name] = select_info.get("name")
            
            elif prop_type == "url":
                # Extract URL
                metadata[prop_name] = prop_data.get("url")
            
            elif prop_type == "status":
                # Extract status
                status_info = prop_data.get("status", {})
                if status_info:
                    metadata[prop_name] = status_info.get("name")
            
            elif prop_type == "number":
                # Extract number
                metadata[prop_name] = prop_data.get("number")
                
        
        metadata["Last Edited Time"] = response.get("last_edited_time")
        metadata["Created Time"] = response.get("created_time")
        
        icon = response.get("icon", {})
        if icon:
            icon_type = icon.get("type")
            if icon_type == "emoji":
                metadata["Icon"] = icon.get("emoji")
            elif icon_type == "external":
                metadata["Icon"] = icon.get("external", {}).get("url")
        
        parent = response.get("parent", {})
        parent_type = parent.get("type")
        if parent_type == "database_id":
            metadata["Parent Database ID"] = parent.get("database_id")
        elif parent_type == "page_id":
            metadata["Parent Page ID"] = parent.get("page_id")
            
        return metadata
    
    
async def demo():
    notion_page_manager = NotionPageManager(page_id="1a3389d5-7bd3-80d7-a507-e67d1b25822c")
    
    # Example usage of the NotionPageManager class
    return await notion_page_manager.get_page_text()

    
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(demo())
    print("result", result)
    