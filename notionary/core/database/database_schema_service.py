from typing import Dict, List
from notionary.core.database.notion_database_schema import NotionDatabaseSchema


class DatabaseSchemaService:
    """Service für den Zugriff auf Datenbankschema-Informationen"""
    
    def __init__(self, schema: NotionDatabaseSchema):
        self._schema = schema
        
    async def get_property_types(self) -> Dict[str, str]:
        """
        Get all property types for the database.

        Returns:
            Dictionary mapping property names to their types
        """
        return await self._schema.get_property_types()
        
    async def get_select_options(self, property_name: str) -> List[Dict[str, str]]:
        """
        Get options for a select, multi-select, or status property.

        Args:
            property_name: Name of the property

        Returns:
            List of select options with name, id, and color (if available)
        """
        options = await self._schema.get_select_options(property_name)
        return [
            {
                "name": option.get("name", ""),
                "id": option.get("id", ""),
                "color": option.get("color", "")
            }
            for option in options
        ]
        
    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, str]]:
        """
        Get available options for a relation property.

        Args:
            property_name: Name of the relation property
            limit: Maximum number of options to retrieve

        Returns:
            List of relation options with id and title
        """
        options = await self._schema.get_relation_options(property_name, limit)
        return [
            {
                "id": option.get("id", ""),
                "title": option.get("title", "")
            }
            for option in options
        ]