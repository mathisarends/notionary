from typing import Dict, List, Optional, Any, Set, TypedDict
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton_decorator import singleton

# Bridge:
# Gucken ob man hiermit gut einen Worklflow Inklusive von Querverntzungen vornhemen kann.
# Weiterhin wie gut man bestimmte Eigenschaften setzen kann ohne den Namen zu haben.
# Vllt. eine Konvention dass man nur eine Property mit einem Type haben darf?  ^^
# Löschen von Seiten nicht nur Erstellen von Seiten aus der Datenbank.

class PropertyInfo(TypedDict, total=False):
    """TypedDict für Eigenschaftsinformationen einer Datenbank."""
    id: str
    name: str
    type: str
    options: List[Dict[str, Any]]
    relation_database_id: str

class DatabaseInfo(TypedDict, total=False):
    """TypedDict für Datenbankinformationen."""
    id: str
    title: str
    url: str
    created_time: str
    last_edited_time: str
    properties: Dict[str, PropertyInfo]
    icon: Optional[Dict[str, Any]]
    cover: Optional[Dict[str, Any]]

@singleton
class NotionDatabaseManager(LoggingMixin):
    """
    Advanced manager for Notion databases with detailed metadata support.
    Caches and manages the structure and properties of each database.
    """
    
    def __init__(self, client: NotionClient):
        """
        Initializes the DatabaseManager with a NotionClient.
        
        Args:
            client: An instance of NotionClient for API requests
        """
        self._client = client
        self._database_details: Dict[str, DatabaseInfo] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Loads all databases and their metadata.
        """
        if self._initialized:
            return
            
        databases = await self._fetch_all_databases()
        
        for db in databases:
            db_id = db.get("id")
            if not db_id:
                continue
                
            db_info: DatabaseInfo = {
                "id": db_id,
                "title": self._extract_database_title(db),
                "url": db.get("url", ""),
                "created_time": db.get("created_time", ""),
                "last_edited_time": db.get("last_edited_time", ""),
                "icon": db.get("icon"),
                "cover": db.get("cover"),
                "properties": {}
            }
            
            db_details = await self._client.api_get(f"databases/{db_id}")
            if db_details and "properties" in db_details:
                db_info["properties"] = self._extract_property_info(db_details["properties"])
            
            self._database_details[db_id] = db_info
                
        self._initialized = True
        self.logger.info("DatabaseManager initialisiert mit %d Datenbanken", len(self._database_details))
    
    async def get_database_info(self, database_id: str) -> Optional[DatabaseInfo]:
        """
        Returns detailed information for a specific database.
        """
        if not self._initialized:
            await self.initialize()
            
        return self._database_details.get(database_id)
    
    async def get_database_title(self, database_id: str) -> Optional[str]:
        """
        Returns the title of a database.
        """
        info = await self.get_database_info(database_id)
        return info.get("title") if info else None
    
    async def get_database_properties(self, database_id: str) -> Dict[str, PropertyInfo]:
        """
        Returns all properties of a database.
        """
        info = await self.get_database_info(database_id)
        return info.get("properties", {}) if info else {}
    
    async def get_property_types(self, database_id: str) -> Dict[str, str]:
        """
        Returns a mapping of property names to their types.
        """
        properties = await self.get_database_properties(database_id)
        return {name: prop.get("type", "") for name, prop in properties.items()}
    
    async def get_property_info(self, database_id: str, property_name: str) -> Optional[PropertyInfo]:
        """
        Returns metadata for a specific property.
        """
        properties = await self.get_database_properties(database_id)
        return properties.get(property_name)
    
    async def get_select_options(self, database_id: str, property_name: str) -> List[Dict[str, Any]]:
        """
        Returns options for a select, multi_select, or status property.
        """
        property_info = await self.get_property_info(database_id, property_name)
        if not property_info:
            return []
            
        return property_info.get("options", [])
        
    async def get_relation_database_id(self, database_id: str, property_name: str) -> Optional[str]:
        """
        Returns the ID of the related database for a relation property.
        """
        property_info = await self.get_property_info(database_id, property_name)
        if not property_info or property_info.get("type") != "relation":
            return None
            
        return property_info.get("relation_database_id")
        
    async def get_relation_options(self, database_id: str, property_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Returns available options for a relation property (i.e., pages in the linked database).
        """
        related_db_id = await self.get_relation_database_id(database_id, property_name)
        if not related_db_id:
            self.logger.warning(f"Keine Relations-Datenbank für {property_name} in {database_id} gefunden")
            return []
            
        result = await self._query_database_pages(related_db_id, limit)
        
        relation_options = []
        for page in result:
            page_id = page.get("id")
            if not page_id:
                continue
                
            page_title = "Unbenannt"
            properties = page.get("properties", {})
            
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title" and "title" in prop_data:
                    title_content = prop_data["title"]
                    if title_content and isinstance(title_content, list):
                        title_parts = []
                        for part in title_content:
                            if "plain_text" in part:
                                title_parts.append(part["plain_text"])
                        if title_parts:
                            page_title = "".join(title_parts)
                            break
            
            relation_options.append({
                "id": page_id,
                "title": page_title
            })
            
        return relation_options
        
    async def _query_database_pages(self, database_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Queries pages in a Notion database.
        """
        pages = []
        start_cursor = None
        page_size = min(limit, 100)  # Notion begrenzt auf 100 pro Anfrage
        remaining = limit
        
        while remaining > 0:
            current_page_size = min(remaining, page_size)
            
            # Erstelle Anfragekörper
            body = {
                "page_size": current_page_size
            }
            
            if start_cursor:
                body["start_cursor"] = start_cursor
                
            # API-Anfrage
            result = await self._client.post(f"databases/{database_id}/query", data=body)
            
            if not result:
                self.logger.error(f"Fehler beim Abfragen der Datenbank {database_id}")
                break
                
            # Verarbeite Ergebnisse
            data = result.data
            if "results" in data and data["results"]:
                pages.extend(data["results"])
                remaining -= len(data["results"])
                
                # Prüfe, ob es weitere Seiten gibt
                if "has_more" in data and data["has_more"] and "next_cursor" in data:
                    start_cursor = data["next_cursor"]
                else:
                    break
            else:
                break
                
        return pages
    
    async def find_databases_by_title(self, title: str, exact_match: bool = False) -> List[str]:
        """
        Finds databases by title.
        """
        if not self._initialized:
            await self.initialize()
            
        results = []
        for db_id, db_info in self._database_details.items():
            db_title = db_info.get("title", "")
            if (exact_match and db_title == title) or (not exact_match and title.lower() in db_title.lower()):
                results.append(db_id)
                
        return results
    
    async def find_databases_by_property_type(self, property_type: str) -> List[str]:
        """
        Finds databases that include a property of the given type.
        """
        if not self._initialized:
            await self.initialize()
            
        results = []
        for db_id, db_info in self._database_details.items():
            properties = db_info.get("properties", {})
            if any(prop.get("type") == property_type for prop in properties.values()):
                results.append(db_id)
                
        return results
    
    async def get_all_database_ids(self) -> List[str]:
        """
        Returns all cached database IDs.
        """
        if not self._initialized:
            await self.initialize()
            
        return list(self._database_details.keys())
    
    async def get_all_property_types(self) -> Set[str]:
        """
        Returns all property types used across all databases.
        """
        if not self._initialized:
            await self.initialize()
            
        property_types = set()
        for db_info in self._database_details.values():
            for prop in db_info.get("properties", {}).values():
                if "type" in prop:
                    property_types.add(prop["type"])
                    
        return property_types
    
    async def refresh(self) -> None:
        """
        Refreshes all cached database metadata.
        """
        self._database_details.clear()
        self._initialized = False
        await self.initialize()
    
    async def refresh_database(self, database_id: str) -> None:
        """
        Refreshes metadata for a specific database.
        """
        if database_id in self._database_details:
            db_details = await self._client.api_get(f"databases/{database_id}")
            if db_details:
                title = self._extract_title_from_api(db_details)
                if title:
                    self._database_details[database_id]["title"] = title
                
                if "last_edited_time" in db_details:
                    self._database_details[database_id]["last_edited_time"] = db_details["last_edited_time"]
                
                if "properties" in db_details:
                    self._database_details[database_id]["properties"] = self._extract_property_info(db_details["properties"])
    
    def _extract_database_title(self, database: Dict[str, Any]) -> str:
        """
        Extracts the database title from a Search API response.
        """
        title = "Unbenannt"
        
        if "title" in database:
            title_parts = []
            for text_obj in database["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])
            
            if title_parts:
                title = "".join(title_parts)
                
        return title
    
    def _extract_title_from_api(self, database: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the title from a direct API response.
        """
        if "title" in database:
            title_parts = []
            for text_obj in database["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])
            
            if title_parts:
                return "".join(title_parts)
        return None
    
    def _extract_property_info(self, properties: Dict[str, Any]) -> Dict[str, PropertyInfo]:
        """
        Extracts property metadata from a database API response.
        """
        result = {}
        
        for name, prop_data in properties.items():
            prop_type = prop_data.get("type", "")
            
            property_info: PropertyInfo = {
                "id": prop_data.get("id", ""),
                "name": name,
                "type": prop_type
            }
            
            if prop_type in ["select", "multi_select", "status"]:
                if prop_type in prop_data and "options" in prop_data[prop_type]:
                    property_info["options"] = prop_data[prop_type]["options"]
            
            # Extrahiere Relations-Informationen
            elif prop_type == "relation" and "relation" in prop_data:
                if "database_id" in prop_data["relation"]:
                    property_info["relation_database_id"] = prop_data["relation"]["database_id"]
            
            result[name] = property_info
            
        return result
    
    async def _fetch_all_databases(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches all Notion databases using the Search API.
        """
        all_databases = []
        start_cursor = None
        
        while True:
            body = {
                "filter": {
                    "value": "database",
                    "property": "object"
                },
                "page_size": page_size
            }
            
            if start_cursor:
                body["start_cursor"] = start_cursor
            
            result = await self._client.post("search", data=body)
            
            if not result:
                self.logger.error("Fehler beim Abrufen der Datenbanken")
                break
            
            data = result.data
            if "results" in data:
                all_databases.extend(data["results"])
            
            if "has_more" in data and data["has_more"] and "next_cursor" in data:
                start_cursor = data["next_cursor"]
            else:
                break
                
        return all_databases
    
async def main():
    client = NotionClient()
    
    try:
        # Manager initialisieren
        db_manager = NotionDatabaseManager(client)
        await db_manager.initialize()
        
        # Beispiel: Datenbank-ID und Property-Name
        database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"  # Deine "Wissen & Notizen" Datenbank
        
        # Alle Relations-Properties finden
        properties = await db_manager.get_database_properties(database_id)
        relation_props = [name for name, info in properties.items() 
                          if info.get("type") == "relation"]
        
        print("Relations-Properties in der Datenbank:")
        for prop_name in relation_props:
            # Für jede Relation die Zieldatenbank und verfügbaren Optionen anzeigen
            related_db_id = await db_manager.get_relation_database_id(database_id, prop_name)
            related_db_title = await db_manager.get_database_title(related_db_id) if related_db_id else "Unbekannt"
            
            print(f"\n- {prop_name} → {related_db_title} ({related_db_id})")
            
            # Abfragen der verfügbaren Relations-Optionen (begrenzt auf 10)
            options = await db_manager.get_relation_options(database_id, prop_name, limit=10)
            
            if options:
                print("  Verfügbare Optionen:")
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option['title']} ({option['id']})")
            else:
                print("  Keine Optionen gefunden oder leere Datenbank")
            
    finally:
        await client.close()
        
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())