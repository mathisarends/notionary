from typing import Any, Dict, List, Optional, Union
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.uuid_utils import is_valid_uuid



class NotionRelationManager(LoggingMixin):
    """
    Manager für Relation-Properties einer Notion-Seite.
    Verwaltet Beziehungen zwischen Seiten und lädt verfügbare Relation-Optionen.
    """

    def __init__(self, page_id: str, client: NotionClient, database_id: Optional[str] = None):
        """
        Initialisiert den Relation-Manager.
        
        Args:
            page_id: ID der Notion-Seite
            client: NotionClient-Instanz
            database_id: Optional, ID der Datenbank, zu der die Seite gehört (wird bei Bedarf geladen)
        """
        self._page_id = page_id
        self._client = client
        self._database_id = database_id
        self._page_properties = None

    async def _get_page_properties(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Lädt die Properties der Seite.
        
        Args:
            force_refresh: Bei True wird ein erneuter API-Call durchgeführt
            
        Returns:
            Dict[str, Any]: Die Properties der Seite
        """
        if self._page_properties is None or force_refresh:
            page_data = await self._client.get_page(self._page_id)
            if page_data and "properties" in page_data:
                self._page_properties = page_data["properties"]
            else:
                self._page_properties = {}
        
        return self._page_properties

    async def _ensure_database_id(self) -> Optional[str]:
        """
        Stellt sicher, dass die database_id vorhanden ist. Lädt sie bei Bedarf.
        
        Returns:
            Optional[str]: Die Datenbank-ID oder None
        """
        if self._database_id:
            return self._database_id
            
        # Versuchen, die Datenbank-ID aus den Seitendaten zu ermitteln
        page_data = await self._client.get_page(self._page_id)
        if page_data and "parent" in page_data:
            parent = page_data["parent"]
            if parent.get("type") == "database_id":
                self._database_id = parent.get("database_id")
                return self._database_id
                
        return None

    async def get_relation_property_ids(self) -> List[str]:
        """
        Gibt eine Liste aller Relation-Property-Namen zurück.
        
        Returns:
            List[str]: Namen aller Relation-Properties
        """
        properties = await self._get_page_properties()
        
        return [
            prop_name for prop_name, prop_data in properties.items()
            if prop_data.get("type") == "relation"
        ]

    async def get_relation_values(self, property_name: str) -> List[str]:
        """
        Gibt die aktuellen Relationswerte für eine Property zurück.
        
        Args:
            property_name: Name der Relation-Property
            
        Returns:
            List[str]: Liste der verknüpften Page-IDs
        """
        properties = await self._get_page_properties()
        
        if property_name not in properties:
            return []
            
        prop_data = properties[property_name]
        
        if prop_data.get("type") != "relation" or "relation" not in prop_data:
            return []
            
        return [rel.get("id") for rel in prop_data["relation"]]

    async def get_relation_details(self, property_name: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Details zur Relation-Property zurück, inkl. verknüpfte Datenbank.
        
        Args:
            property_name: Name der Relation-Property
            
        Returns:
            Optional[Dict[str, Any]]: Details zur Relation oder None
        """
        database_id = await self._ensure_database_id()
        if not database_id:
            return None
            
        try:
            database = await self._client.get(f"databases/{database_id}")
            if not database or "properties" not in database:
                return None
                
            properties = database["properties"]
            
            if property_name not in properties:
                return None
                
            prop_data = properties[property_name]
            
            if prop_data.get("type") != "relation":
                return None
                
            return prop_data.get("relation", {})
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Relation-Details: {str(e)}")
            return None

    async def get_relation_database_id(self, property_name: str) -> Optional[str]:
        """
        Gibt die ID der verknüpften Datenbank für eine Relation-Property zurück.
        
        Args:
            property_name: Name der Relation-Property
            
        Returns:
            Optional[str]: ID der verknüpften Datenbank oder None
        """
        relation_details = await self.get_relation_details(property_name)
        
        if not relation_details:
            return None
            
        return relation_details.get("database_id")

    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Gibt verfügbare Optionen für eine Relation-Property zurück.
        
        Args:
            property_name: Name der Relation-Property
            limit: Maximale Anzahl der zurückzugebenden Optionen
            
        Returns:
            List[Dict[str, Any]]: Liste der verfügbaren Optionen mit ID und Name
        """
        related_db_id = await self.get_relation_database_id(property_name)
        
        if not related_db_id:
            return []
            
        try:
            # Abfrage der verknüpften Datenbank
            query_result = await self._client.post(
                f"databases/{related_db_id}/query",
                {
                    "page_size": limit,
                }
            )
            
            if not query_result or "results" not in query_result:
                return []
                
            # Relevante Informationen aus den Seiten extrahieren
            options = []
            for page in query_result["results"]:
                page_id = page.get("id")
                title = self._extract_title_from_page(page)
                
                if page_id and title:
                    options.append({
                        "id": page_id,
                        "name": title
                    })
                    
            return options
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Relation-Optionen: {str(e)}")
            return []

    def _extract_title_from_page(self, page: Dict[str, Any]) -> Optional[str]:
        """
        Extrahiert den Titel aus einem Page-Objekt.
        
        Args:
            page: Das Page-Objekt von der Notion API
            
        Returns:
            Optional[str]: Der Seitentitel oder None
        """
        if "properties" not in page:
            return None
            
        properties = page["properties"]
        
        # Nach einer Title-Property suchen
        for prop_data in properties.values():
            if prop_data.get("type") == "title" and "title" in prop_data:
                title_parts = prop_data["title"]
                return "".join([text_obj.get("plain_text", "") for text_obj in title_parts])
                
        return None

    async def add_relation(self, property_name: str, page_ids: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        Fügt eine oder mehrere Relationen hinzu.
        
        Args:
            property_name: Name der Relation-Property
            page_ids: Eine Page-ID oder Liste von Page-IDs
            
        Returns:
            Optional[Dict[str, Any]]: API-Antwort oder None bei Fehler
        """
        existing_relations = await self.get_relation_values(property_name) or []
        
        if isinstance(page_ids, str):
            page_ids = [page_ids]
            
        # Bestehende und neue Relationen kombinieren, Duplikate entfernen
        all_relations = list(set(existing_relations + page_ids))
        
        # Property-Payload erstellen
        relation_payload = {
            "relation": [{"id": page_id} for page_id in all_relations]
        }
        
        try:
            result = await self._client.patch(
                f"pages/{self._page_id}",
                {
                    "properties": {
                        property_name: relation_payload
                    }
                },
            )
            
            # Cache aktualisieren
            self._page_properties = None
            
            return result
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Relation: {str(e)}")
            return None
        
    async def add_relation_by_name(self, property_name: str, page_titles: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        Fügt eine oder mehrere Relationen anhand von Seitennamen hinzu.
        
        Args:
            property_name: Name der Relation-Property
            pages: Ein Page-Titel oder Liste von Page-Titeln
                
        Returns:
            Optional[Dict[str, Any]]: API-Antwort oder None bei Fehler
        """
        if isinstance(page_titles, str):
            page_titles = [page_titles]
        
        page_ids = []
        for page in page_titles:
            if is_valid_uuid(page):
                page_ids.append(page)
            else:
                page_id = await self._get_page_id_by_title(page)
                if page_id:
                    page_ids.append(page_id)
                else:
                    self.logger.warning("Keine Seite mit Titel '%s' gefunden", page)
        
        # Existierende add_relation Methode verwenden
        if page_ids:
            return await self.add_relation(property_name, page_ids)
        
        self.logger.warning("Keine gültigen Page-IDs gefunden, keine Änderungen vorgenommen")
        return None

    async def _get_page_id_by_title(self, title: str) -> Optional[str]:
        search_results = await self._client.post(
            "search",
            {
                "query": title,
                "filter": {
                    "value": "page",
                    "property": "object"
                }
            }
        )

        print("search_results", search_results)

        for result in search_results.get("results", []):
            properties = result.get("properties", {})

            for prop_value in properties.values():
                if prop_value.get("type") == "title":
                    title_texts = prop_value.get("title", [])
                    page_title = " ".join([t.get("plain_text", "") for t in title_texts])

                    if page_title == title or title in page_title:
                        print(f"Seite gefunden: '{page_title}' mit ID: {result.get('id')}")
                        return result.get("id")

        print(f"Keine Seite mit Titel '{title}' gefunden")
        return None


    async def set_relations(self, property_name: str, page_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Setzt die Relationen auf die angegebenen IDs (ersetzt bestehende).
        
        Args:
            property_name: Name der Relation-Property
            page_ids: Liste der Page-IDs, die gesetzt werden sollen
            
        Returns:
            Optional[Dict[str, Any]]: API-Antwort oder None bei Fehler
        """
        # Property-Payload erstellen
        relation_payload = {
            "relation": [{"id": page_id} for page_id in page_ids]
        }
        
        try:
            result = await self._client.patch(
                f"pages/{self._page_id}",
                {
                    "properties": {
                        property_name: relation_payload
                    }
                },
            )
            
            # Cache aktualisieren
            self._page_properties = None
            
            return result
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen der Relationen: {str(e)}")
            return None