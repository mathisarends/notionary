from typing import Dict, List, Optional, Any, Tuple
from notionary.notion_client import NotionClient
from notionary.util import LoggingMixin


class DatabasePropertyService(LoggingMixin):
    """
    Service for working with Notion database properties and options.
    Provides specialized methods for retrieving property information and validating values.
    """

    def __init__(self, database_id: str, client: NotionClient):
        """
        Initialize the database property service.

        Args:
            database_id: ID of the Notion database
            client: Instance of NotionClient
        """
        self._database_id = database_id
        self._client = client
        self._schema = None

    async def load_schema(self, force_refresh: bool = False) -> bool:
        """
        Loads the database schema.

        Args:
            force_refresh: Whether to force a refresh of the schema

        Returns:
            True if schema loaded successfully, False otherwise.
        """
        if self._schema is not None and not force_refresh:
            return True

        try:
            database = await self._client.get_database(self._database_id)

            self._schema = database.properties
            self.logger.debug("Loaded schema for database %s", self._database_id)
            return True

        except Exception as e:
            self.logger.error(
                "Error loading database schema for %s: %s", self._database_id, str(e)
            )
            return False

    async def _ensure_schema_loaded(self) -> None:
        """
        Ensures the schema is loaded before accessing it.
        """
        if self._schema is None:
            await self.load_schema()

    async def get_schema(self) -> Dict[str, Any]:
        """
        Gets the database schema.

        Returns:
            Dict[str, Any]: The database schema
        """
        await self._ensure_schema_loaded()
        return self._schema or {}

    async def get_property_types(self) -> Dict[str, str]:
        """
        Gets all property types for the database.

        Returns:
            Dict[str, str]: Dictionary mapping property names to their types
        """
        await self._ensure_schema_loaded()

        if not self._schema:
            return {}

        return {
            prop_name: prop_data.get("type", "unknown")
            for prop_name, prop_data in self._schema.items()
        }

    async def get_property_schema(self, property_name: str) -> Optional[Dict[str, Any]]:
        """
        Gets the schema for a specific property.

        Args:
            property_name: The name of the property

        Returns:
            Optional[Dict[str, Any]]: The property schema or None if not found
        """
        await self._ensure_schema_loaded()

        if not self._schema or property_name not in self._schema:
            return None

        return self._schema[property_name]

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """
        Gets the type of a specific property.

        Args:
            property_name: The name of the property

        Returns:
            Optional[str]: The property type or None if not found
        """
        property_schema = await self.get_property_schema(property_name)

        if not property_schema:
            return None

        return property_schema.get("type")

    async def property_exists(self, property_name: str) -> bool:
        """
        Checks if a property exists in the database.

        Args:
            property_name: The name of the property

        Returns:
            bool: True if the property exists, False otherwise
        """
        property_schema = await self.get_property_schema(property_name)
        return property_schema is not None

    async def get_property_options(self, property_name: str) -> List[Dict[str, Any]]:
        """
        Gets the available options for a property (select, multi_select, status).

        Args:
            property_name: The name of the property

        Returns:
            List[Dict[str, Any]]: List of available options with their metadata
        """
        property_schema = await self.get_property_schema(property_name)

        if not property_schema:
            return []

        property_type = property_schema.get("type")

        if property_type in ["select", "multi_select", "status"]:
            return property_schema.get(property_type, {}).get("options", [])

        return []

    async def get_option_names(self, property_name: str) -> List[str]:
        """
        Gets the available option names for a property (select, multi_select, status).

        Args:
            property_name: The name of the property

        Returns:
            List[str]: List of available option names
        """
        options = await self.get_property_options(property_name)
        return [option.get("name", "") for option in options]

    async def get_relation_details(
        self, property_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Gets details about a relation property, including the related database.

        Args:
            property_name: The name of the property

        Returns:
            Optional[Dict[str, Any]]: The relation details or None if not a relation
        """
        property_schema = await self.get_property_schema(property_name)

        if not property_schema or property_schema.get("type") != "relation":
            return None

        return property_schema.get("relation", {})

    async def get_relation_options(
        self, property_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Gets available options for a relation property by querying the related database.

        Args:
            property_name: The name of the relation property
            limit: Maximum number of options to retrieve

        Returns:
            List[Dict[str, Any]]: List of pages from the related database
        """
        relation_details = await self.get_relation_details(property_name)

        if not relation_details or "database_id" not in relation_details:
            return []

        related_db_id = relation_details["database_id"]

        try:
            # Query the related database to get options
            query_result = await self._client.post(
                f"databases/{related_db_id}/query",
                {
                    "page_size": limit,
                },
            )

            if not query_result or "results" not in query_result:
                return []

            # Extract relevant information from each page
            options = []
            for page in query_result["results"]:
                page_id = page.get("id")
                title = self._extract_title_from_page(page)

                if page_id and title:
                    options.append({"id": page_id, "name": title})

            return options
        except Exception as e:
            self.logger.error(f"Error getting relation options: {str(e)}")
            return []

    def _extract_title_from_page(self, page: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the title from a page object.

        Args:
            page: The page object from Notion API

        Returns:
            Optional[str]: The page title or None if not found
        """
        if "properties" not in page:
            return None

        properties = page["properties"]

        # Look for a title property
        for prop_data in properties.values():
            if prop_data.get("type") == "title" and "title" in prop_data:
                title_parts = prop_data["title"]
                return "".join(
                    [text_obj.get("plain_text", "") for text_obj in title_parts]
                )

        return None

    async def validate_property_value(
        self, property_name: str, value: Any
    ) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Validates a value for a property.

        Args:
            property_name: The name of the property
            value: The value to validate

        Returns:
            Tuple[bool, Optional[str], Optional[List[str]]]:
                - Boolean indicating if valid
                - Error message if invalid
                - Available options if applicable
        """
        property_schema = await self.get_property_schema(property_name)

        if not property_schema:
            return False, f"Property '{property_name}' does not exist", None

        property_type = property_schema.get("type")

        # Validate select, multi_select, status properties
        if property_type in ["select", "status"]:
            options = await self.get_option_names(property_name)

            if isinstance(value, str) and value not in options:
                return (
                    False,
                    f"Invalid {property_type} option. Value '{value}' is not in the available options.",
                    options,
                )

        elif property_type == "multi_select":
            options = await self.get_option_names(property_name)

            if isinstance(value, list):
                invalid_values = [val for val in value if val not in options]
                if invalid_values:
                    return (
                        False,
                        f"Invalid multi_select options: {', '.join(invalid_values)}",
                        options,
                    )

        return True, None, None
