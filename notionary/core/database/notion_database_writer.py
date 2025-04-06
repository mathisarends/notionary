from typing import Any, Dict, List, Optional, Union, TypedDict, cast
from notionary.core.database.notion_database_manager import NotionDatabaseSchema
from notionary.core.notion_client import NotionClient
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin


class NotionRelationItem(TypedDict):
    id: str


class NotionRelationProperty(TypedDict):
    relation: List[NotionRelationItem]


class NotionFormattedValue(TypedDict, total=False):
    title: List[Dict[str, Any]]
    rich_text: List[Dict[str, Any]]
    select: Dict[str, str]
    multi_select: List[Dict[str, str]]
    relation: List[NotionRelationItem]
    number: Union[int, float]
    date: Dict[str, str]
    checkbox: bool
    url: str
    email: str
    phone_number: str


class PageCreationResponse(TypedDict):
    id: str
    parent: Dict[str, str]
    properties: Dict[str, Any]


class NotionRelationHandler(LoggingMixin):
    """
    Handler for managing relations in Notion databases.
    Provides a unified interface for working with relations.
    """

    def __init__(self, client: NotionClient, db_schema: NotionDatabaseSchema) -> None:
        self._client = client
        self._db_schema = db_schema
        self._formatter = NotionPropertyFormatter()

    async def find_relation_by_title(
        self, database_id: str, relation_prop_name: str, title: str
    ) -> Optional[str]:
        """
        Finds a relation ID based on the title of the entry in the target database.
        """
        target_db_id = await self._db_schema.get_relation_database_id(
            relation_prop_name
        )
        if not target_db_id:
            self.logger.error(
                "No target database found for relation '%s' in database %s",
                relation_prop_name,
                database_id,
            )
            return None

        options = await self._db_schema.get_relation_options(relation_prop_name)

        for option in options:
            if option["title"].lower() == title.lower():
                self.logger.debug("Relation entry '%s' found: %s", title, option["id"])
                return option["id"]

        self.logger.warning("Relation entry '%s' not found", title)
        return None

    async def _get_title_properties(
        self, database_id: str, title: str
    ) -> Optional[Dict[str, NotionFormattedValue]]:
        """
        Determines the title property for a database and formats the value.
        """
        if not await self._db_schema.load():
            self.logger.error("Could not load database schema for %s", database_id)
            return None

        property_types = await self._db_schema.get_property_types()

        title_prop_name: Optional[str] = None
        for name, prop_type in property_types.items():
            if prop_type == "title":
                title_prop_name = name
                break

        if not title_prop_name:
            self.logger.error("No title property found in database %s", database_id)
            return None

        formatted_title = self._formatter.format_value("title", title)
        if not formatted_title:
            self.logger.error("Could not format title '%s'", title)
            return None

        return {title_prop_name: cast(NotionFormattedValue, formatted_title)}


class DatabaseWritter(LoggingMixin):
    """
    Enhanced class for creating and updating pages in Notion databases.
    Supports both simple properties and relations.
    """

    def __init__(
        self, client: NotionClient, db_schema: Optional[NotionDatabaseSchema] = None
    ) -> None:
        """
        Initialize with a NotionClient and optionally a NotionDatabaseSchema.

        Args:
            client: The Notion API client
            db_schema: Optional database schema instance
        """
        self._client = client
        self._formatter = NotionPropertyFormatter()

        self._active_schema: Optional[NotionDatabaseSchema] = db_schema
        self._relation_handler: Optional[NotionRelationHandler] = None

        if db_schema:
            self._relation_handler = NotionRelationHandler(client, db_schema)

    async def _ensure_schema_for_database(self, database_id: str) -> bool:
        """
        Stellt sicher, dass ein Schema für die angegebene Datenbank geladen ist.

        Args:
            database_id: ID der Datenbank

        Returns:
            True, wenn das Schema erfolgreich geladen wurde
        """
        if self._active_schema and self._active_schema.database_id == database_id:
            return True

        self._active_schema = NotionDatabaseSchema(database_id, self._client)
        self._relation_handler = NotionRelationHandler(
            self._client, self._active_schema
        )

        return await self._active_schema.load()

    async def create_page(
        self,
        database_id: str,
        properties: Dict[str, Any],
        relations: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Optional[PageCreationResponse]:
        """
        Creates a new page in a database with support for relations.
        """
        # Stelle sicher, dass wir ein Schema für diese Datenbank haben
        if not await self._ensure_schema_for_database(database_id):
            self.logger.error("Could not load schema for database %s", database_id)
            return None

        formatted_props = await self._format_properties(database_id, properties)
        if not formatted_props:
            return None

        if relations:
            relation_props = await self._process_relations(database_id, relations)
            if relation_props:
                formatted_props.update(relation_props)

        data: Dict[str, Any] = {
            "parent": {"database_id": database_id},
            "properties": formatted_props,
        }

        result = await self._client.post("pages", data)
        if not result:
            self.logger.error("Error creating page in database %s", database_id)
            return None

        self.logger.info("Page successfully created in database %s", database_id)
        return cast(PageCreationResponse, result)

    async def update_page(
        self,
        page_id: str,
        properties: Optional[Dict[str, Any]] = None,
        relations: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Updates a page with support for relations.
        """
        page_data = await self._client.get(f"pages/{page_id}")
        if (
            not page_data
            or "parent" not in page_data
            or "database_id" not in page_data["parent"]
        ):
            self.logger.error("Could not determine database ID for page %s", page_id)
            return None

        database_id = page_data["parent"]["database_id"]

        # Stelle sicher, dass wir ein Schema für diese Datenbank haben
        if not await self._ensure_schema_for_database(database_id):
            self.logger.error("Could not load schema for database %s", database_id)
            return None

        if not properties and not relations:
            self.logger.warning("No properties or relations specified for update")
            return page_data

        update_props: Dict[str, NotionFormattedValue] = {}

        if properties:
            formatted_props = await self._format_properties(database_id, properties)
            if formatted_props:
                update_props.update(formatted_props)

        if relations:
            relation_props = await self._process_relations(database_id, relations)
            if relation_props:
                update_props.update(relation_props)

        if not update_props:
            self.logger.warning("No valid properties to update for page %s", page_id)
            return None

        data = {"properties": update_props}

        result = await self._client.patch(f"pages/{page_id}", data)
        if not result:
            self.logger.error("Error updating page %s", page_id)
            return None

        self.logger.info("Page %s successfully updated", page_id)
        return result

    async def delete_page(self, page_id: str) -> bool:
        """
        Deletes a page (archives it in Notion).
        """
        data = {"archived": True}

        result = await self._client.patch(f"pages/{page_id}", data)
        if not result:
            self.logger.error("Error deleting page %s", page_id)
            return False

        self.logger.info("Page %s successfully deleted (archived)", page_id)
        return True

    async def _format_properties(
        self, database_id: str, properties: Dict[str, Any]
    ) -> Optional[Dict[str, NotionFormattedValue]]:
        """
        Formats properties according to their types in the database.
        """
        if not self._active_schema:
            self.logger.error("No active schema available for database %s", database_id)
            return None

        property_types = await self._active_schema.get_property_types()
        if not property_types:
            self.logger.error(
                "Could not get property types for database %s", database_id
            )
            return None

        formatted_props: Dict[str, NotionFormattedValue] = {}

        for prop_name, value in properties.items():
            if prop_name not in property_types:
                self.logger.warning(
                    "Property '%s' does not exist in database %s",
                    prop_name,
                    database_id,
                )
                continue

            prop_type = property_types[prop_name]

            formatted_value = self._formatter.format_value(prop_type, value)
            if formatted_value:
                formatted_props[prop_name] = cast(NotionFormattedValue, formatted_value)
            else:
                self.logger.warning(
                    "Could not format value for property '%s' of type '%s'",
                    prop_name,
                    prop_type,
                )

        return formatted_props

    async def _process_relations(
        self, database_id: str, relations: Dict[str, Union[str, List[str]]]
    ) -> Dict[str, NotionRelationProperty]:
        """
        Processes relation properties and converts titles to IDs.
        """
        if not self._relation_handler:
            self.logger.error("No relation handler available")
            return {}

        formatted_relations: Dict[str, NotionRelationProperty] = {}
        property_types = (
            await self._active_schema.get_property_types()
            if self._active_schema
            else {}
        )

        for prop_name, titles in relations.items():
            relation_property = await self._process_single_relation(
                database_id, prop_name, titles, property_types
            )
            if relation_property:
                formatted_relations[prop_name] = relation_property

        return formatted_relations

    async def _process_single_relation(
        self,
        database_id: str,
        prop_name: str,
        titles: Union[str, List[str]],
        property_types: Dict[str, str],
    ) -> Optional[NotionRelationProperty]:
        """
        Process a single relation property and convert titles to IDs.

        Args:
            database_id: The database ID
            prop_name: The property name
            titles: The title or list of titles to convert
            property_types: Dictionary of property types

        Returns:
            A formatted relation property or None if invalid
        """
        if prop_name not in property_types:
            self.logger.warning(
                "Property '%s' does not exist in database %s", prop_name, database_id
            )
            return None

        prop_type = property_types[prop_name]
        if prop_type != "relation":
            self.logger.warning(
                "Property '%s' is not a relation (type: %s)", prop_name, prop_type
            )
            return None

        title_list: List[str] = [titles] if isinstance(titles, str) else titles
        relation_ids = await self._get_relation_ids(database_id, prop_name, title_list)

        if not relation_ids:
            return None

        return {"relation": [{"id": rel_id} for rel_id in relation_ids]}

    async def _get_relation_ids(
        self, database_id: str, prop_name: str, titles: List[str]
    ) -> List[str]:
        """
        Get relation IDs for a list of titles.

        Args:
            database_id: The database ID
            prop_name: The property name
            titles: List of titles to convert

        Returns:
            List of relation IDs
        """
        relation_ids: List[str] = []

        for title in titles:
            relation_id = await self._relation_handler.find_relation_by_title(
                database_id, prop_name, title
            )

            if relation_id:
                relation_ids.append(relation_id)
            else:
                self.logger.warning(
                    "Could not find relation ID for '%s' in '%s'", title, prop_name
                )

        return relation_ids
