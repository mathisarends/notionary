import asyncio
from notionary.core.notion_client import NotionClient
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin
from typing import Any, Dict, List, Optional

class NotionMetadataManager(LoggingMixin):
    """Optimierter Manager für Notion-Seiteneigenschaften."""
    
    def __init__(self, page_id: str, token: Optional[str] = None):
        self._client = NotionClient(token=token)
        self.page_id = page_id
        self._properties_cache = {}
        self._formatter = NotionPropertyFormatter()
        self._is_building_cache = False
        self._metadata = None
    
    async def get_page_metadata(self) -> Optional[Dict[str, Any]]:
        if self._metadata:
            return self._metadata
            
        result = await self._client.get(f"pages/{self.page_id}")
        
        if not result:
            self.logger.error("Fehler beim Abrufen der Seitenmetadaten: %s", result.error)
            return None
        
        page_data = result.data
        self._metadata = page_data
        
        if "properties" in page_data and not self._is_building_cache:
            await self._build_properties_cache(page_data["properties"])
        
        return page_data
    
    async def _build_properties_cache(self, properties: Dict[str, Any]) -> None:
        """
        Erstellt einen detaillierten Cache mit Eigenschaftsinformationen.
        """
        self._is_building_cache = True
        
        try:
            for name, prop_data in properties.items():
                prop_id = prop_data.get("id")
                prop_type = prop_data.get("type")
                
                self._properties_cache[name] = {
                    "id": prop_id,
                    "type": prop_type,
                    "data": prop_data.get(prop_type, {})
                }
            
            if self._metadata and "parent" in self._metadata and "database_id" in self._metadata["parent"]:
                database_id = self._metadata["parent"]["database_id"]
                await self._enrich_status_properties(database_id)
        finally:
            self._is_building_cache = False
    
    async def _enrich_status_properties(self, database_id: str) -> None:
        """Füge Status-Optionen zu Status-Eigenschaften hinzu."""
        status_props = [name for name, info in self._properties_cache.items()
                         if info.get("type") == "status" and "options" not in info]
        
        if not status_props:
            return
            
        database_schema = await self._get_database_schema(database_id)
        if not database_schema or "properties" not in database_schema:
            return
            
        for prop_name in status_props:
            prop_info = self._properties_cache[prop_name]
            prop_id = prop_info["id"]
            
            for db_prop_name, db_prop in database_schema["properties"].items():
                if db_prop.get("type") != "status" or db_prop.get("id") != prop_id:
                    continue
                    
                if "status" in db_prop and "options" in db_prop["status"]:
                    self._properties_cache[prop_name]["options"] = db_prop["status"]["options"]
    
    async def _get_database_schema(self, database_id: str) -> Optional[Dict[str, Any]]:
        """Ruft das Schema einer Notion-Datenbank ab."""
        result = await self._client.get(f"databases/{database_id}")
        
        if not result:
            self.logger.error("Fehler beim Abrufen des Datenbankschemas: %s", result.error)
            return None
        
        return result.data
    
    async def get_status_options(self, status_property_name: str) -> List[Dict[str, Any]]:
        """
        Gibt die verfügbaren Optionen für eine Status-Eigenschaft zurück.
        """
        if not self._properties_cache:
            await self.get_page_metadata()
        
        if status_property_name not in self._properties_cache:
            self.logger.error("Eigenschaft '%s' nicht gefunden", status_property_name)
            return []
        
        prop_info = self._properties_cache[status_property_name]
        if prop_info["type"] != "status":
            self.logger.error("Eigenschaft '%s' ist keine Status-Eigenschaft", status_property_name)
            return []
        
        # Wenn wir die Optionen bereits gecacht haben, geben wir sie zurück
        if "options" in prop_info:
            return prop_info["options"]
        
        # Optionen abrufen, wenn wir die Datenbank-ID haben
        if self._metadata and "parent" in self._metadata and "database_id" in self._metadata["parent"]:
            database_id = self._metadata["parent"]["database_id"]
            await self._enrich_status_properties(database_id)
            
            # Nochmal prüfen, ob wir jetzt Optionen haben
            if "options" in prop_info:
                return prop_info["options"]
        
        # Keine Optionen gefunden
        return []
    
    async def update_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Aktualisiert den Titel einer Notion-Seite."""
        formatted_title = self._formatter.format_title(title)
        properties = {
            "title": formatted_title["title"]
        }
        
        return await self.update_properties(properties)
    
    async def update_properties(self, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Aktualisiert die Eigenschaften einer Notion-Seite."""
        result = await self._client.patch(f"pages/{self.page_id}", {"properties": properties})
        
        if not result:
            self.logger.error("Fehler beim Aktualisieren der Eigenschaften: %s", result.error)
            return None
        
        # Metadaten-Cache aktualisieren
        self._metadata = None
        
        return result.data
    
    async def update_property_by_name(self, name: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Aktualisiert eine Eigenschaft anhand ihres Namens mit Typ-Validierung.
        """
        # Metadaten abrufen, wenn wir noch keinen Eigenschafts-Cache haben
        if not self._properties_cache:
            await self.get_page_metadata()
        
        if name not in self._properties_cache:
            self.logger.error("Eigenschaft '%s' nicht gefunden", name)
            return None
        
        prop_info = self._properties_cache[name]
        prop_type = prop_info["type"]
        
        if prop_type == "status":
            status_options = await self.get_status_options(name)
            status_names = [option["name"] for option in status_options]
            
            if status_names and str(value) not in status_names:
                self.logger.error("Ungültiger Status: '%s'. Verfügbare Optionen: %s", 
                                 value, ', '.join(status_names))
                return None
        
        formatted_prop = self._formatter.format_value(prop_type, value)
        if not formatted_prop:
            return None
        
        properties = {
            name: formatted_prop
        }
        
        return await self.update_properties(properties)
    
    async def set_page_icon(self, emoji: Optional[str] = None, 
                          external_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not emoji and not external_url:
            self.logger.error("Entweder emoji oder external_url muss angegeben werden")
            return None
        
        if emoji:
            icon = {"type": "emoji", "emoji": emoji}
        else:
            icon = {"type": "external", "external": {"url": external_url}}
        
        result = await self._client.patch(f"pages/{self.page_id}", {"icon": icon})
        
        if not result:
            self.logger.error("Fehler beim Setzen des Seiten-Icons: %s", result.error)
            return None
        
        # Metadaten-Cache aktualisieren
        self._metadata = None
        
        return result.data
    
    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        cover = {"type": "external", "external": {"url": external_url}}
        result = await self._client.patch(f"pages/{self.page_id}", {"cover": cover})
        
        if not result:
            self.logger.error("Fehler beim Setzen des Seiten-Covers: %s", result.error)
            return None
        
        self._metadata = None
        
        return result.data
    
    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Setzt den Titel einer Notion-Seite."""
        properties = {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        result = await self._client.patch(f"pages/{self.page_id}", {"properties": properties})
        
        if not result:
            self.logger.error("Fehler beim Setzen des Titels: %s", result.error)
            return None
        
        self._metadata = None
        
        return result.data
    
    async def find_property_by_type(self, prop_type: str) -> List[str]:
        """Findet alle Eigenschaften eines bestimmten Typs."""
        if not self._properties_cache:
            await self.get_page_metadata()
        
        return [name for name, info in self._properties_cache.items() 
                if info.get("type") == prop_type]
    
    async def list_valid_status_options(self, status_property_name: str) -> List[str]:
        """
        Gibt eine Liste aller gültigen Status-Optionen für eine Status-Eigenschaft zurück.
        """
        options = await self.get_status_options(status_property_name)
        return [option["name"] for option in options]


# Demo-Funktion
async def run_demo():
    page_id = "1c8389d5-7bd3-814a-974e-f9e706569b16"
    
    manager = NotionMetadataManager(page_id=page_id)
    
    metadata = await manager.get_page_metadata()
    if not metadata:
        print("Konnte keine Metadaten abrufen.")
        return
        
    print("Verfügbare Eigenschaften:")
    for name, info in manager._properties_cache.items():
        prop_type = info.get("type")
        print(f"- {name} (Typ: {prop_type})")
    
    # 2. Icon und Cover setzen
    print("\nSetze Icon und Cover...")
    await manager.set_page_icon(emoji="🎧")
    await manager.set_page_cover("https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4")
    await manager.set_title("Soundcore Retoure")
    
    # 3. Status-Optionen auflisten und gültigen Status setzen
    status_props = await manager.find_property_by_type("status")
    if status_props:
        status_name = status_props[0]
        valid_options = await manager.list_valid_status_options(status_name)
        
        print(f"\nVerfügbare Status-Optionen für '{status_name}':")
        for option in valid_options:
            print(f"- {option}")
        
        if valid_options:
            # Ersten verfügbaren Status verwenden
            print(f"\nAktualisiere Status auf: {valid_options[3]}")
            await manager.update_property_by_name(status_name, valid_options[3])
    
    # 4. URL aktualisieren
    url_props = await manager.find_property_by_type("url")
    if url_props:
        url_name = url_props[0]
        print(f"\nAktualisiere URL-Eigenschaft: {url_name}")
        await manager.update_property_by_name(url_name, "https://www.soundcore.com/updates")
    
    # 5. Tags (Multi-Select) aktualisieren
    multi_select_props = await manager.find_property_by_type("multi_select")
    if multi_select_props:
        tags_name = multi_select_props[0]
        print(f"\nAktualisiere Tags-Eigenschaft: {tags_name}")
        await manager.update_property_by_name(tags_name, ["Kopfhörer", "Bestellung"])
    
    print("\nAktualisierung abgeschlossen!")


# Führe die Demo aus
if __name__ == "__main__":
    asyncio.run(run_demo())