from typing import Any, Dict, Optional
from notionary.notion_client import NotionClient
from notionary.page.properites.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin


class MetadataEditor(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
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

    async def set_property(
        self, property_name: str, property_value: Any, property_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generic method to set any property on a Notion page.

        Args:
            property_name: The name of the property in Notion
            property_value: The value to set
            property_type: The type of property ('select', 'multi_select', 'status', 'relation', etc.)

        Returns:
            Optional[Dict[str, Any]]: The API response or None if the operation fails
        """
        property_payload = self._property_formatter.format_value(
            property_type, property_value
        )

        if not property_payload:
            self.logger.warning(
                "Could not create payload for property type: %s", property_type
            )
            return None

        return await self._client.patch(
            f"pages/{self.page_id}",
            {"properties": {property_name: property_payload}},
        )

    async def get_property_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves the schema for all properties of the page.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping property names to their schema
        """
        page_data = await self._client.get_page(self.page_id)
        property_schema = {}

        for prop_name, prop_data in page_data.properties.items():
            # Annahme: prop_data ist immer noch ein Dict
            prop_type = prop_data.get("type")
            property_schema[prop_name] = {
                "id": prop_data.get("id"),
                "type": prop_type,
                "name": prop_name,
            }

            try:
                if prop_type == "select" and "select" in prop_data:
                    # Make sure prop_data["select"] is a dictionary before calling .get()
                    if isinstance(prop_data["select"], dict):
                        property_schema[prop_name]["options"] = prop_data["select"].get(
                            "options", []
                        )
                elif prop_type == "multi_select" and "multi_select" in prop_data:
                    # Make sure prop_data["multi_select"] is a dictionary before calling .get()
                    if isinstance(prop_data["multi_select"], dict):
                        property_schema[prop_name]["options"] = prop_data[
                            "multi_select"
                        ].get("options", [])
                elif prop_type == "status" and "status" in prop_data:
                    # Make sure prop_data["status"] is a dictionary before calling .get()
                    if isinstance(prop_data["status"], dict):
                        property_schema[prop_name]["options"] = prop_data["status"].get(
                            "options", []
                        )
            except Exception as e:
                if hasattr(self, "logger") and self.logger:
                    self.logger.warning(
                        "Error processing property schema for '%s': %s", prop_name, e
                    )

        return property_schema

    async def set_property_by_name(
        self, property_name: str, value: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Sets a property value based on the property name, automatically detecting the property type.

        Args:
            property_name: The name of the property in Notion
            value: The value to set

        Returns:
            Optional[Dict[str, Any]]: The API response or None if the operation fails
        """
        property_schema = await self.get_property_schema()

        if property_name not in property_schema:
            self.logger.warning(
                "Property '%s' not found in database schema", property_name
            )
            return None

        property_type = property_schema[property_name]["type"]
        return await self.set_property(property_name, value, property_type)
