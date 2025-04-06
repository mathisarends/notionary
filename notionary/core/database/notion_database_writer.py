from typing import Any, Dict, List, Optional
from notionary.core.database.notion_database_manager import NotionDatabaseManager
from notionary.core.notion_client import NotionClient
from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton_decorator import singleton

@singleton
class NotionDatabaseWriter(LoggingMixin):
    """
    Vereinfachte Klasse zum Erstellen und Aktualisieren von Seiten in Notion-Datenbanken.
    Nutzt den vorhandenen NotionPropertyFormatter für die Wert-Formatierung.
    """
    
    def __init__(self, client: NotionClient):
        """
        Initialisiert den DatabaseWriter mit einem NotionClient.
        
        Args:
            client: Eine Instanz des NotionClient für API-Anfragen
        """
        self._client = client
        self._formatter = NotionPropertyFormatter()
    
    async def create_page(self, database_id: str, properties: Dict[str, Any], 
                         content: List[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Erstellt eine neue Seite in einer Datenbank.
        
        Args:
            database_id: ID der Datenbank
            properties: Dictionary mit Eigenschaftsnamen und Werten (unformatiert)
            content: Liste von Inhaltsblöcken (optional)
            
        Returns:
            Die erstellte Seite oder None bei Fehler
        """
        formatted_props = await self._format_properties(database_id, properties)
        if not formatted_props:
            return None
            
        data = {
            "parent": {
                "database_id": database_id
            },
            "properties": formatted_props
        }
        
        # Füge Inhaltsblöcke hinzu, wenn vorhanden
        if content:
            data["children"] = content
            
        result = await self._client.api_post("pages", data)
        if not result:
            self.logger.error("Fehler beim Erstellen einer Seite in Datenbank %s", database_id)
            return None
            
        self.logger.info("Seite in Datenbank %s erfolgreich erstellt", database_id)
        return result
    
    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Aktualisiert die Eigenschaften einer Seite.
        
        Args:
            page_id: ID der Seite
            properties: Dictionary mit Eigenschaftsnamen und Werten (unformatiert)
            
        Returns:
            Die aktualisierte Seite oder None bei Fehler
        """
        page_data = await self._client.api_get(f"pages/{page_id}")
        if not page_data or "parent" not in page_data or "database_id" not in page_data["parent"]:
            self.logger.error("Konnte Datenbank-ID für Seite %s nicht ermitteln", page_id)
            return None
            
        database_id = page_data["parent"]["database_id"]
        
        formatted_props = await self._format_properties(database_id, properties)
        if not formatted_props:
            return None
            
        data = {
            "properties": formatted_props
        }
        
        result = await self._client.api_patch(f"pages/{page_id}", data)
        if not result:
            self.logger.error("Fehler beim Aktualisieren der Seite %s", page_id)
            return None
            
        self.logger.info("Seite %s erfolgreich aktualisiert", page_id)
        return result
    
    async def _format_properties(self, database_id: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Formatiert Eigenschaften entsprechend ihrer Typen in der Datenbank.
        
        Args:
            database_id: ID der Datenbank
            properties: Dictionary mit Eigenschaftsnamen und unformatierten Werten
            
        Returns:
            Dictionary mit formatierten Eigenschaften oder None bei Fehler
        """
        db_schema = await self._client.api_get(f"databases/{database_id}")
        if not db_schema or "properties" not in db_schema:
            self.logger.error("Konnte Datenbankschema für %s nicht laden", database_id)
            return None
        
        formatted_props = {}
        
        for prop_name, value in properties.items():
            if prop_name not in db_schema["properties"]:
                self.logger.warning("Eigenschaft '%s' existiert nicht in Datenbank %s", prop_name, database_id)
                continue
                
            prop_type = db_schema["properties"][prop_name]["type"]
            
            formatted_value = self._formatter.format_value(prop_type, value)
            if formatted_value:
                formatted_props[prop_name] = formatted_value
            else:
                self.logger.warning("Konnte Wert für Eigenschaft '%s' vom Typ '%s' nicht formatieren", prop_name, prop_type)
        
        return formatted_props
    
    
async def main():
    client = NotionClient()
    
    try:
        db_manager = NotionDatabaseManager(client)
        db_writer = NotionDatabaseWriter(client)
        
        await db_manager.initialize()
        
        # Datenbank-ID
        database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a" 
        
        new_page = await db_writer.create_page(
            database_id=database_id,
            properties={
                "Name": "Neue Notiz über XanaX",
                "Tags": ["Python", "Programmierung"],
                "Status": "Entwurf",
                "URL": "https://www.python.org"
            }
        )
        
        if new_page:
            page_id = new_page["id"]

            page_manager = NotionPageManager(page_id=page_id)
            await page_manager.set_page_icon(emoji="📝")
            await page_manager.append_markdown("thats not it")
            
    finally:
        await client.close()
        
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())