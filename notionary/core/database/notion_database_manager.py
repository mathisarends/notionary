from typing import Dict, List, Optional, Any
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin

class NotionDatabaseManager(LoggingMixin):
    def __init__(self, client: NotionClient):
        self._client = client
        self._databases_map = {}
        self._databases_cache = []
        self._initialized = False
    
    async def initialize(self) -> None:
        if self._initialized:
            return
            
        databases = await self._fetch_all_databases()
        self._databases_cache = databases
        
        for db in databases:
            db_id = db.get("id")
            title = self._extract_database_title(db)
            if db_id and title:
                self._databases_map[db_id] = title
                
        self._initialized = True
        self.logger.info("DatabaseManager initialisiert mit %d Datenbanken", len(self._databases_map))
    
    async def get_database_title(self, database_id: str) -> Optional[str]:
        if not self._initialized:
            await self.initialize()
            
        return self._databases_map.get(database_id)
    
    async def get_database_ids_by_title(self, title: str, exact_match: bool = False) -> List[str]:
        if not self._initialized:
            await self.initialize()
            
        if exact_match:
            return [db_id for db_id, db_title in self._databases_map.items() if db_title == title]

        return [db_id for db_id, db_title in self._databases_map.items() if title.lower() in db_title.lower()]
    
    async def get_all_databases(self, refresh: bool = False) -> List[Dict[str, Any]]:
        if refresh or not self._initialized:
            await self.initialize()
            
        return self._databases_cache
    
    async def get_database_map(self) -> Dict[str, str]:
        if not self._initialized:
            await self.initialize()
            
        return self._databases_map.copy()
    
    async def refresh(self) -> None:
        self._initialized = False
        await self.initialize()
    
    def _extract_database_title(self, database: Dict[str, Any]) -> str:
        title = "Unbenannt"
        
        if "title" in database:
            title_parts = []
            for text_obj in database["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])
            
            if title_parts:
                title = "".join(title_parts)
                
        return title
    
    async def _fetch_all_databases(self, page_size: int = 100) -> List[Dict[str, Any]]:
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
        db_manager = NotionDatabaseManager(client)
        
        await db_manager.initialize()
        
        db_map = await db_manager.get_database_map()
        print(f"Gefundene Datenbanken: {len(db_map)}")
        for db_id, title in db_map.items():
            print(f"ID: {db_id}, Titel: {title}")
        
    finally:
        await client.close()
        
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())