import re
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Callable
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.core.database.notion_database_manager import NotionDatabaseSchema
from notionary.core.database.notion_database_manager import NotionDatabaseRegistry


class NotionDatabaseManager(LoggingMixin):
    """
    High-Level Fassade zur Verwaltung von Notion-Datenbanken und deren Einträgen.
    Bietet vereinfachte Methoden zum Erstellen, Lesen, Aktualisieren und Löschen von Datenbankeinträgen.
    """

    def __init__(
        self,
        database_id: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """
        Initialisiert den Datenbank-Manager mit einer Datenbank-ID oder URL.

        Args:
            database_id: Die ID der Notion-Datenbank
            url: Die URL der Notion-Datenbank (alternativ zur ID)
            token: Optional - ein benutzerdefiniertes API-Token
        """
        if not database_id and not url:
            raise ValueError("Either database_id or url must be provided")

        if not database_id and url:
            database_id = self._extract_notion_uuid(url)
            if not database_id:
                raise ValueError(
                    f"Could not extract a valid UUID from the URL: {url}"
                )

        if not self._validate_uuid_format(database_id):
            parsed_id = self._extract_notion_uuid(database_id)
            if not parsed_id:
                raise ValueError(
                    f"Invalid UUID format and could not be parsed: {database_id}"
                )
            database_id = parsed_id

        self.database_id = database_id
        self.url = url

        self._client = NotionClient(token=token)
        self._schema = NotionDatabaseSchema(database_id, self._client)
        self._writer = DatabaseWritter(self._client, self._schema)
        self._registry = NotionDatabaseRegistry(self._client)

    async def get_schema(self) -> Dict[str, str]:
        """
        Gibt das Schema der Datenbank zurück (Eigenschaften und ihre Typen).

        Returns:
            Ein Dictionary mit Eigenschaftsnamen und ihren Typen
        """
        await self._schema.load()
        return await self._schema.get_property_types()

    async def get_select_options(self, property_name: str) -> List[Dict[str, str]]:
        """
        Ruft die verfügbaren Optionen für eine Select-, Multi-Select- oder Status-Eigenschaft ab.

        Args:
            property_name: Der Name der Eigenschaft

        Returns:
            Eine Liste von Optionsobjekten mit Namen und IDs
        """
        return await self._schema.get_select_options(property_name)

    async def create_entry(
        self, 
        properties: Dict[str, Any], 
        relations: Optional[Dict[str, Union[str, List[str]]]] = None
    ) -> Optional[str]:
        """
        Erstellt einen neuen Eintrag in der Datenbank.

        Args:
            properties: Ein Dictionary mit Eigenschaftsnamen und Werten
            relations: Optional - ein Dictionary mit Relationsnamen und Titeln der verknüpften Einträge

        Returns:
            Die ID des erstellten Eintrags oder None bei Fehler
        """
        result = await self._writer.create_page(self.database_id, properties, relations)
        if result:
            self.logger.info("Entry created with ID: %s", result['id'])
            return result["id"]
        return None

    async def update_entry(
        self, 
        page_id: str, 
        properties: Optional[Dict[str, Any]] = None,
        relations: Optional[Dict[str, Union[str, List[str]]]] = None
    ) -> bool:
        """
        Aktualisiert einen bestehenden Eintrag in der Datenbank.

        Args:
            page_id: Die ID des zu aktualisierenden Eintrags
            properties: Ein Dictionary mit zu aktualisierenden Eigenschaften und Werten
            relations: Optional - ein Dictionary mit zu aktualisierenden Relationen

        Returns:
            True bei Erfolg, False bei Fehler
        """
        result = await self._writer.update_page(page_id, properties, relations)
        return result is not None

    async def delete_entry(self, page_id: str) -> bool:
        """
        Löscht (archiviert) einen Eintrag aus der Datenbank.

        Args:
            page_id: Die ID des zu löschenden Eintrags

        Returns:
            True bei Erfolg, False bei Fehler
        """
        return await self._writer.delete_page(page_id)

    async def get_entries(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        transform: Optional[Callable[[Dict[str, Any]], Any]] = None
    ) -> List[Any]:
        """
        Ruft Einträge aus der Datenbank ab mit optionalen Filtern und Sortierung.

        Args:
            filter_conditions: Optional - Filterbedingungen für die Abfrage
            sorts: Optional - Sortierungsanweisungen für die Abfrage
            limit: Optional - maximale Anzahl der abzurufenden Einträge
            transform: Optional - eine Funktion zur Transformation der Ergebnisse

        Returns:
            Eine Liste von Datenbankeinträgen oder transformierten Werten
        """
        entries = []
        count = 0
        
        async for page in self.iter_entries(filter_conditions, sorts):
            if limit and count >= limit:
                break
                
            if transform:
                entries.append(transform(page))
            else:
                entries.append(page)
                
            count += 1
            
        return entries

    async def iter_entries(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        page_size: int = 100
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Asynchroner Generator, der Einträge aus der Datenbank schrittweise zurückgibt.

        Args:
            filter_conditions: Optional - Filterbedingungen für die Abfrage
            sorts: Optional - Sortierungsanweisungen für die Abfrage
            page_size: Die Anzahl der Einträge, die pro Anfrage abgerufen werden sollen

        Yields:
            Einzelne Datenbankeinträge aus der Notion-API
        """
        async for page in self._schema.iter_database_pages(
            page_size=page_size,
            filter_conditions=filter_conditions,
            sorts=sorts
        ):
            yield page

    async def create_status_filter(self, property_name: str, status_value: str) -> Dict[str, Any]:
        """
        Erstellt eine Filterbedingung für eine Status-Eigenschaft.

        Args:
            property_name: Der Name der Status-Eigenschaft
            status_value: Der Statuswert, nach dem gefiltert werden soll

        Returns:
            Ein Filter-Dictionary für die Verwendung mit get_entries oder iter_entries
        """
        return {
            "property": property_name,
            "status": {
                "equals": status_value
            }
        }

    async def create_title_filter(self, title_value: str, contains: bool = True) -> Dict[str, Any]:
        """
        Erstellt eine Filterbedingung für den Titel.

        Args:
            title_value: Der Titelwert, nach dem gefiltert werden soll
            contains: True für eine enthält-Abfrage, False für eine exakte Übereinstimmung

        Returns:
            Ein Filter-Dictionary für die Verwendung mit get_entries oder iter_entries
        """
        condition = "contains" if contains else "equals"
        return {
            "property": "title",
            "title": {
                condition: title_value
            }
        }

    async def create_number_filter(
        self, 
        property_name: str, 
        condition: str, 
        value: Union[int, float]
    ) -> Dict[str, Any]:
        """
        Erstellt eine Filterbedingung für eine Zahleneigenschaft.

        Args:
            property_name: Der Name der Zahleneigenschaft
            condition: Die Bedingung (z.B. "equals", "greater_than", "less_than")
            value: Der Zahlenwert für den Vergleich

        Returns:
            Ein Filter-Dictionary für die Verwendung mit get_entries oder iter_entries
        """
        return {
            "property": property_name,
            "number": {
                condition: value
            }
        }

    async def get_related_entries(
        self, 
        property_name: str, 
        related_title: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Findet Einträge, die mit einem bestimmten Eintrag durch eine Relation verknüpft sind.

        Args:
            property_name: Der Name der Relationseigenschaft
            related_title: Der Titel des verknüpften Eintrags
            limit: Maximale Anzahl der abzurufenden Einträge

        Returns:
            Eine Liste von verknüpften Einträgen
        """
        # Finde zuerst die ID des verwandten Eintrags
        related_db_id = await self._schema.get_relation_database_id(property_name)
        if not related_db_id:
            self.logger.error("No related database found for property %s", property_name)
            return []
            
        related_schema = NotionDatabaseSchema(related_db_id, self._client)
        
        related_id = None
        async for page in related_schema.iter_database_pages():
            title = related_schema.extract_title_from_page(page)
            if title.lower() == related_title.lower():
                related_id = page["id"]
                break
                
        if not related_id:
            self.logger.warning("No entry with title '%s' found in related database", related_title)
            return []
            
        # Dann finde alle Einträge, die auf diesen Eintrag verweisen
        filter_conditions = {
            "property": property_name,
            "relation": {
                "contains": related_id
            }
        }
        
        return await self.get_entries(filter_conditions=filter_conditions, limit=limit)

    @staticmethod
    def _extract_notion_uuid(url: str) -> Optional[str]:
        """Extrahiert die UUID aus einer Notion-URL."""
        uuid_pattern = r"([a-f0-9]{32})"
        match = re.search(uuid_pattern, url.lower())

        if not match:
            return None

        uuid_raw = match.group(1)
        formatted_uuid = f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"

        return formatted_uuid

    @staticmethod
    def _validate_uuid_format(uuid: str) -> bool:
        """Überprüft, ob eine Zeichenfolge dem UUID-Format entspricht."""
        uuid_pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
        return bool(re.match(uuid_pattern, uuid.lower()))