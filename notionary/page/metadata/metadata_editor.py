from typing import Any, Dict, Optional
from notionary.page.client import NotionPageClient
from notionary.page.properites.property_formatter import NotionPropertyFormatter
from notionary.util import LoggingMixin


class MetadataEditor(LoggingMixin):
    """
    Manages and edits the metadata and properties of a Notion page.
    """

    def __init__(self, page_id: str, client: NotionPageClient):
        """
        Initialize the metadata editor.

        Args:
            page_id: The ID of the Notion page
            client: The Notion API client
        """
        self.page_id = page_id
        self._client = client
        self._property_formatter = NotionPropertyFormatter()

    async def set_title(self, title: str) -> Optional[str]:
        """
        Sets the title of the page.

        Args:
            title: The new title for the page.

        Returns:
            Optional[str]: The new title if successful, None otherwise.
        """
        try:
            data = {
                "properties": {
                    "title": {"title": [{"type": "text", "text": {"content": title}}]}
                }
            }

            result = await self._client.patch_page(self.page_id, data)

            if result:
                return title
            return None
        except Exception as e:
            self.logger.error("Error setting page title: %s", str(e))
            return None

    async def set_property_by_name(
        self, property_name: str, value: Any
    ) -> Optional[str]:
        """
        Sets a property value based on the property name, automatically detecting the property type.

        Args:
            property_name: The name of the property in Notion
            value: The value to set

        Returns:
            Optional[str]: The property name if successful, None if operation fails
        """
        property_schema = await self._get_property_schema()

        if property_name not in property_schema:
            self.logger.warning(
                "Property '%s' not found in database schema", property_name
            )
            return None

        property_type = property_schema[property_name]["type"]
        return await self._set_property(property_name, value, property_type)

    async def _set_property(
        self, property_name: str, property_value: Any, property_type: str
    ) -> Optional[str]:
        """
        Generic method to set any property on a Notion page.

        Args:
            property_name: The name of the property in Notion
            property_value: The value to set
            property_type: The type of property ('select', 'multi_select', 'status', 'relation', etc.)

        Returns:
            Optional[str]: The property name if successful, None if operation fails
        """
        property_payload = self._property_formatter.format_value(
            property_type, property_value
        )

        if not property_payload:
            self.logger.warning(
                "Could not create payload for property type: %s", property_type
            )
            return None

        try:
            result = await self._client.patch_page(
                self.page_id, {"properties": {property_name: property_payload}}
            )

            if result:
                return property_name
            return None
        except Exception as e:
            self.logger.error("Error setting property '%s': %s", property_name, str(e))
            return None

    async def _get_property_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves the schema for all properties of the page.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping property names to their schema
        """
        page_data = await self._client.get_page(self.page_id)
        property_schema = {}

        # Property types that can have options
        option_types = {
            "select": "select",
            "multi_select": "multi_select",
            "status": "status",
        }

        for prop_name, prop_data in page_data.properties.items():
            prop_type = prop_data.get("type")

            schema_entry = {
                "id": prop_data.get("id"),
                "type": prop_type,
                "name": prop_name,
            }

            # Check if this property type can have options
            if prop_type in option_types:
                option_key = option_types[prop_type]
                try:
                    prop_type_data = prop_data.get(option_key, {})
                    if isinstance(prop_type_data, dict):
                        schema_entry["options"] = prop_type_data.get("options", [])
                except Exception as e:
                    self.logger.warning(
                        "Error processing property schema for '%s': %s", prop_name, e
                    )

            property_schema[prop_name] = schema_entry

        return property_schema
