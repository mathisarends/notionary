from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.meta_data.metadata_cache import MetadataCache
from notionary.core.page.meta_data.metadata_property_manager import MetadataPropertManager
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin

class MetaDataPropertySetter(LoggingMixin):
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
        
        self.properties = MetadataPropertManager(self._client, self._cache, self._formatter)
        self.content = MetaDataPropertySetter(self._client, self._cache)
        
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


