import asyncio
from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin

class MetadataCache(LoggingMixin):
    """Verwaltet den Metadaten-Cache für Notion-Seiten."""
    
    def __init__(self, client: NotionClient):
        self._client = client
        self._page_metadata = {}
        self._property_cache = {}
        self._is_building_cache = False
    
    def get_cached_metadata(self, page_id: str) -> Optional[Dict[str, Any]]:
        return self._page_metadata.get(page_id)
    
    def set_cached_metadata(self, page_id: str, metadata: Dict[str, Any]) -> None:
        self._page_metadata[page_id] = metadata
    
    def clear_metadata(self, page_id: str) -> None:
        if page_id in self._page_metadata:
            del self._page_metadata[page_id]
    
    def get_property_cache(self, page_id: str) -> Dict[str, Any]:
        if page_id not in self._property_cache:
            self._property_cache[page_id] = {}
        return self._property_cache[page_id]
    
    def set_property_data(self, page_id: str, prop_name: str, data: Dict[str, Any]) -> None:
        if page_id not in self._property_cache:
            self._property_cache[page_id] = {}
        self._property_cache[page_id][prop_name] = data
    
    def is_building_cache(self) -> bool:
        return self._is_building_cache
    
    def set_building_cache(self, value: bool) -> None:
        self._is_building_cache = value


class PropertyManager(LoggingMixin):
    """Verwaltet Eigenschaften von Notion-Seiten."""
    
    def __init__(self, client: NotionClient, cache: MetadataCache, formatter: NotionPropertyFormatter):
        self._client = client
        self._cache = cache
        self._formatter = formatter
    
    async def find_property_by_type(self, page_id: str, prop_type: str) -> List[str]:
        """Findet alle Eigenschaften eines bestimmten Typs."""
        properties = self._cache.get_property_cache(page_id)
        if not properties:
            self.logger.warning("Keine Eigenschaften im Cache für Seite %s", page_id)
            return []
        
        return [name for name, info in properties.items() 
                if info.get("type") == prop_type]
    
    async def get_status_options(self, page_id: str, status_property_name: str) -> List[Dict[str, Any]]:
        """Gibt die verfügbaren Optionen für eine Status-Eigenschaft zurück."""
        properties = self._cache.get_property_cache(page_id)
        
        if not properties:
            self.logger.warning("Keine Eigenschaften im Cache für Seite %s", page_id)
            return []
        
        if status_property_name not in properties:
            self.logger.error("Eigenschaft '%s' nicht gefunden", status_property_name)
            return []
        
        prop_info = properties[status_property_name]
        if prop_info["type"] != "status":
            self.logger.error("Eigenschaft '%s' ist keine Status-Eigenschaft", status_property_name)
            return []
        
        if "options" in prop_info:
            return prop_info["options"]
            
        return []
    
    async def list_valid_status_options(self, page_id: str, status_property_name: str) -> List[str]:
        """Gibt eine Liste aller gültigen Status-Optionen-Namen zurück."""
        options = await self.get_status_options(page_id, status_property_name)
        return [option["name"] for option in options]
    
    async def update_property(self, page_id: str, name: str, value: Any) -> Optional[Dict[str, Any]]:
        """Aktualisiert eine einzelne Eigenschaft mit Typ-Validierung."""
        properties = self._cache.get_property_cache(page_id)
        
        if name not in properties:
            self.logger.error("Eigenschaft '%s' nicht gefunden", name)
            return None
        
        prop_info = properties[name]
        prop_type = prop_info["type"]
        
        if prop_type == "status":
            status_options = await self.get_status_options(page_id, name)
            status_names = [option["name"] for option in status_options]
            
            if status_names and str(value) not in status_names:
                self.logger.error("Ungültiger Status: '%s'. Verfügbare Optionen: %s", 
                                 value, ', '.join(status_names))
                return None
        
        formatted_prop = self._formatter.format_value(prop_type, value)
        if not formatted_prop:
            return None
        
        properties_data = {
            name: formatted_prop
        }
        
        result = await self._client.api_patch(f"pages/{page_id}", {"properties": properties_data})
        
        if result:
            self._cache.clear_metadata(page_id)
            
        return result


class PageContentManager(LoggingMixin):
    """Verwaltet den Inhalt von Notion-Seiten (Titel, Icon, Cover)."""
    
    def __init__(self, client: NotionClient, cache: MetadataCache):
        self._client = client
        self._cache = cache
    
    async def set_title(self, page_id: str, title: str) -> Optional[Dict[str, Any]]:
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
        
        result = await self._client.api_patch(f"pages/{page_id}", {"properties": properties})
        
        if result:
            self._cache.clear_metadata(page_id)
            
        return result
    
    async def set_icon(self, page_id: str, emoji: Optional[str] = None, 
                     external_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Setzt das Icon für eine Notion-Seite."""
        if not emoji and not external_url:
            self.logger.error("Entweder emoji oder external_url muss angegeben werden")
            return None
        
        if emoji:
            icon = {"type": "emoji", "emoji": emoji}
        else:
            icon = {"type": "external", "external": {"url": external_url}}
        
        result = await self._client.api_patch(f"pages/{page_id}", {"icon": icon})
        
        if result:
            self._cache.clear_metadata(page_id)
            
        return result
    
    async def set_cover(self, page_id: str, external_url: str) -> Optional[Dict[str, Any]]:
        """Setzt das Cover-Bild für eine Notion-Seite."""
        cover = {"type": "external", "external": {"url": external_url}}
        
        result = await self._client.api_patch(f"pages/{page_id}", {"cover": cover})
        
        if result:
            self._cache.clear_metadata(page_id)
            
        return result


class NotionMetadataManager(LoggingMixin):
    """Hauptklasse für die Verwaltung von Notion-Seitenmetadaten."""
    
    def __init__(self, page_id: str, token: Optional[str] = None):
        self._client = NotionClient(token=token)
        self.page_id = page_id
        
        self._cache = MetadataCache(self._client)
        self._formatter = NotionPropertyFormatter()
        
        self.properties = PropertyManager(self._client, self._cache, self._formatter)
        self.content = PageContentManager(self._client, self._cache)
        
    @property
    def cache(self) -> MetadataCache:
        return self._cache
    
    async def get_page_metadata(self) -> Optional[Dict[str, Any]]:
        """Ruft die Metadaten einer Notion-Seite ab und cached sie."""
        cached_metadata = self._cache.get_cached_metadata(self.page_id)
        if cached_metadata:
            return cached_metadata
            
        metadata = await self._client.api_get(f"pages/{self.page_id}")
        
        if not metadata:
            return None
        
        self._cache.set_cached_metadata(self.page_id, metadata)
        
        # Eigenschaften-Cache aufbauen, wenn nicht bereits dabei
        if "properties" in metadata and not self._cache.is_building_cache():
            await self._build_properties_cache(metadata["properties"])
        
        return metadata
    
    async def _build_properties_cache(self, properties: Dict[str, Any]) -> None:
        """Erstellt einen Cache mit Eigenschaftsinformationen."""
        self._cache.set_building_cache(True)
        
        try:
            for name, prop_data in properties.items():
                prop_id = prop_data.get("id")
                prop_type = prop_data.get("type")
                
                self._cache.set_property_data(self.page_id, name, {
                    "id": prop_id,
                    "type": prop_type,
                    "data": prop_data.get(prop_type, {})
                })
            
            await self._load_status_options_if_needed()
        finally:
            self._cache.set_building_cache(False)
    
    async def _load_status_options_if_needed(self) -> None:
        """Lädt Status-Optionen für Status-Eigenschaften, falls nötig."""
        metadata = self._cache.get_cached_metadata(self.page_id)
        if not metadata or "parent" not in metadata or "database_id" not in metadata["parent"]:
            return
        
        db_id = metadata["parent"]["database_id"]
        
        properties = self._cache.get_property_cache(self.page_id)
        status_props = [name for name, info in properties.items()
                        if info.get("type") == "status" and "options" not in info]
                        
        if not status_props:
            return
            
        database_schema = await self._client.api_get(f"databases/{db_id}")
        if not database_schema or "properties" not in database_schema:
            return
            
        for prop_name in status_props:
            await self._add_status_options_to_property(prop_name, database_schema)
    
    async def _add_status_options_to_property(self, prop_name: str, database_schema: Dict[str, Any]) -> None:
        """Fügt Status-Optionen zu einer bestimmten Eigenschaft hinzu."""
        properties = self._cache.get_property_cache(self.page_id)
        if prop_name not in properties:
            return
            
        prop_info = properties[prop_name]
        prop_id = prop_info["id"]
        
        for db_prop_name, db_prop in database_schema["properties"].items():
            if db_prop.get("type") != "status" or db_prop.get("id") != prop_id:
                continue
                
            if "status" in db_prop and "options" in db_prop["status"]:
                prop_info["options"] = db_prop["status"]["options"]
                self._cache.set_property_data(self.page_id, prop_name, prop_info)
                break
    
    async def find_property_by_type(self, prop_type: str) -> List[str]:
        """Findet alle Eigenschaften eines bestimmten Typs."""
        await self.get_page_metadata()
        return await self.properties.find_property_by_type(self.page_id, prop_type)
    
    async def update_property_by_name(self, name: str, value: Any) -> Optional[Dict[str, Any]]:
        """Aktualisiert eine einzelne Eigenschaft."""
        await self.get_page_metadata()
        return await self.properties.update_property(self.page_id, name, value)
    
    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self.content.set_title(self.page_id, title)
    
    async def set_page_icon(self, emoji: Optional[str] = None, external_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return await self.content.set_icon(self.page_id, emoji, external_url)
    
    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self.content.set_cover(self.page_id, external_url)
    
    async def list_valid_status_options(self, status_property_name: str) -> List[str]:
        await self.get_page_metadata()
        return await self.properties.list_valid_status_options(self.page_id, status_property_name)
    
    async def close(self):
        """Schließt den HTTP-Client und gibt Ressourcen frei."""
        await self._client.close()


# Demo-Funktion
async def run_demo():
    page_id = "1c8389d5-7bd3-814a-974e-f9e706569b16"
    
    manager = NotionMetadataManager(page_id=page_id)
    
    try:
        metadata = await manager.get_page_metadata()
        if not metadata:
            print("Konnte keine Metadaten abrufen.")
            return
            
        print("Verfügbare Eigenschaften:")
        for name, info in manager.cache.get_property_cache(page_id).items():
            prop_type = info.get("type")
            print(f"- {name} (Typ: {prop_type})")
        
        # Icon und Cover setzen über den PageContentManager
        print("\nSetze Icon und Cover...")
        await manager.set_page_icon(emoji="🎧")
        await manager.set_page_cover("https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4")
        await manager.set_title("Soundcore Retoure")
        
        # Status-Optionen auflisten und gültigen Status setzen über den PropertyManager
        status_props = await manager.find_property_by_type("status")
        if status_props:
            status_name = status_props[0]
            valid_options = await manager.list_valid_status_options(status_name)
            
            print(f"\nVerfügbare Status-Optionen für '{status_name}':")
            for option in valid_options:
                print(f"- {option}")
            
            if valid_options:
                option_index = min(3, len(valid_options) - 1)
                status_to_set = valid_options[option_index]
                print(f"\nAktualisiere Status auf: {status_to_set}")
                await manager.update_property_by_name(status_name, status_to_set)
        
        # URL aktualisieren
        url_props = await manager.find_property_by_type("url")
        if url_props:
            url_name = url_props[0]
            print(f"\nAktualisiere URL-Eigenschaft: {url_name}")
            await manager.update_property_by_name(url_name, "https://www.soundcore.com/updates")
        
        # Tags (Multi-Select) aktualisieren
        multi_select_props = await manager.find_property_by_type("multi_select")
        if multi_select_props:
            tags_name = multi_select_props[0]
            print(f"\nAktualisiere Tags-Eigenschaft: {tags_name}")
            await manager.update_property_by_name(tags_name, ["Kopfhörer", "Bestellung"])
        
        print("\nAktualisierung abgeschlossen!")
    
    finally:
        # Sicherstellen, dass Ressourcen freigegeben werden
        await manager.close()


# Führe die Demo aus
if __name__ == "__main__":
    asyncio.run(run_demo())