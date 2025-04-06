from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.meta_data.metadata_cache import MetadataCache
from notionary.core.page.meta_data.metadata_property_manager import MetadataPropertManager
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin

class PageMetadataProvider(LoggingMixin):
    """Verwaltet Metadaten und Eigenschaften von Notion-Seiten mit optimiertem Datenbank-Caching."""
    
    _database_schema_cache = {}
    
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client
        self._cache = MetadataCache(client)
        self._formatter = NotionPropertyFormatter()
        self._properties = MetadataPropertManager(client, self._cache, self._formatter)

    async def get_page_metadata(self) -> Optional[Dict[str, Any]]:
        """Lädt Metadaten einer Seite mit optimiertem Caching."""
        cached = self._cache.get_cached_metadata(self.page_id)
        if cached:
            return cached

        metadata = await self._client.api_get(f"pages/{self.page_id}")
        if not metadata:
            return None

        self._cache.set_cached_metadata(self.page_id, metadata)

        if self._is_page_in_database(metadata=metadata):
            db_id = metadata["parent"]["database_id"]
            if db_id not in self._database_schema_cache:
                await self._load_database_schema(db_id)

        if "properties" in metadata and not self._cache.is_building_cache():
            await self._build_properties_cache(metadata["properties"])

        return metadata

    async def _load_database_schema(self, db_id: str) -> None:
        """Lädt das Schema einer Datenbank und speichert es im Cache."""
        database_schema = await self._client.api_get(f"databases/{db_id}")
        if database_schema and "properties" in database_schema:
            self._database_schema_cache[db_id] = database_schema
            self.logger.debug("Datenbankschema für %s in den Cache geladen", db_id)

    async def _build_properties_cache(self, properties: Dict[str, Any]) -> None:
        """Baut den Cache für die Eigenschaften einer Seite auf."""
        self._cache.set_building_cache(True)
        try:
            for name, prop_data in properties.items():
                prop_id = prop_data.get("id")
                prop_type = prop_data.get("type")
                prop_value = prop_data.get(prop_type, {})
                
                self._cache.set_property_data(self.page_id, name, {
                    "id": prop_id,
                    "type": prop_type,
                    "data": prop_value
                })

            # Lade Options für Status-Properties, wenn nötig
            await self._enrich_properties_from_db_schema()
        finally:
            self._cache.set_building_cache(False)

    async def _enrich_properties_from_db_schema(self) -> None:
        """Ergänzt die Property-Informationen mit Daten aus dem Datenbankschema."""
        metadata = self._cache.get_cached_metadata(self.page_id)
        if not metadata or "parent" not in metadata or "database_id" not in metadata["parent"]:
            return

        db_id = metadata["parent"]["database_id"]
        
        if db_id not in self._database_schema_cache:
            await self._load_database_schema(db_id)
            if db_id not in self._database_schema_cache:
                return
        
        database_schema = self._database_schema_cache[db_id]
        
        properties = self._cache.get_property_cache(self.page_id)
        
        status_props = [name for name, info in properties.items()
                        if info.get("type") == "status" and "options" not in info]
        
        print("status_props", status_props)
        
        for prop_name in status_props:
            await self._add_options_to_property(prop_name, "status", database_schema)
        
        multi_select_props = [name for name, info in properties.items()
                             if info.get("type") == "multi_select" and "options" not in info]
        
        print("multi_select_props", multi_select_props)
        
        for prop_name in multi_select_props:
            await self._add_options_to_property(prop_name, "multi_select", database_schema)
        
        select_props = [name for name, info in properties.items()
                       if info.get("type") == "select" and "options" not in info]
        
        print("select_props", select_props)
        
        for prop_name in select_props:
            await self._add_options_to_property(prop_name, "select", database_schema)

    async def _add_options_to_property(self, prop_name: str, prop_type: str, database_schema: Dict[str, Any]) -> None:
        """Fügt die verfügbaren Optionen zu einer Eigenschaft hinzu."""
        properties = self._cache.get_property_cache(self.page_id)
        if prop_name not in properties:
            return

        prop_info = properties[prop_name]
        prop_id = prop_info["id"]

        for db_prop_name, db_prop in database_schema["properties"].items():
            if db_prop.get("type") != prop_type or db_prop.get("id") != prop_id:
                continue

            # Verarbeite je nach Typ die Optionen
            if prop_type in db_prop and "options" in db_prop[prop_type]:
                prop_info["options"] = db_prop[prop_type]["options"]
                self._cache.set_property_data(self.page_id, prop_name, prop_info)
                self.logger.debug("Optionen für %s-Property '%s' hinzugefügt", prop_type, prop_name)
                break

    async def update_property_by_name(self, name: str, value: Any) -> Optional[Dict[str, Any]]:
        """Aktualisiert eine Eigenschaft anhand ihres Namens."""
        await self.get_page_metadata()
        return await self._properties.update_property(self.page_id, name, value)

    async def list_valid_status_options(self, name: str) -> List[str]:
        """Gibt eine Liste aller gültigen Status-Optionen für eine Eigenschaft zurück."""
        await self.get_page_metadata()
        return await self._properties.list_valid_status_options(self.page_id, name)

    async def find_property_by_type(self, prop_type: str) -> List[str]:
        """Findet alle Eigenschaften eines bestimmten Typs."""
        await self.get_page_metadata()
        return await self._properties.find_property_by_type(self.page_id, prop_type)
        
    async def get_database_id(self) -> Optional[str]:
        """Gibt die Datenbank-ID zurück, zu der diese Seite gehört (falls vorhanden)."""
        metadata = await self.get_page_metadata()
        if metadata and "parent" in metadata and "database_id" in metadata["parent"]:
            return metadata["parent"]["database_id"]
        return None
        
    async def get_database_schema(self) -> Optional[Dict[str, Any]]:
        """Gibt das Schema der Datenbank zurück, zu der diese Seite gehört (falls vorhanden)."""
        db_id = await self.get_database_id()
        if not db_id:
            return None
            
        if db_id not in self._database_schema_cache:
            await self._load_database_schema(db_id)
            
        return self._database_schema_cache.get(db_id)
    
    def _is_page_in_database(self, metadata: Dict[str, Any]) -> bool:
        """Überprüft, ob die Seite in einer Datenbank ist."""
        return "parent" in metadata and "database_id" in metadata["parent"]
