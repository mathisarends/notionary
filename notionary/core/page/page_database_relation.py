from typing import Dict, List, Optional, Any
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class PageDatabaseRelation(LoggingMixin):
    """
    Manages the relationship between a Notion page and its parent database.
    Provides methods to access database schema and property options.
    """
    
    def __init__(self, page_id: str, client: NotionClient):
        """
        Initialize the page-database relationship handler.
        
        Args:
            page_id: ID of the Notion page
            client: Instance of NotionClient
        """
        self._page_id = page_id
        self._client = client
        self._parent_database_id = None
        self._database_schema = None
        self._page_data = None
    
    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
        """
        Gets the page data and caches it for future use.
        
        Args:
            force_refresh: Whether to force a refresh of the page data
            
        Returns:
            Dict[str, Any]: The page data
        """
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data
    
    async def get_parent_database_id(self) -> Optional[str]:
        """
        Gets the ID of the database this page belongs to, if any.
        
        Returns:
            Optional[str]: The database ID or None if the page doesn't belong to a database
        """
        if self._parent_database_id is not None:
            return self._parent_database_id
            
        page_data = await self._get_page_data()
        
        if not page_data or "parent" not in page_data:
            return None
            
        parent = page_data.get("parent", {})
        if parent.get("type") == "database_id":
            self._parent_database_id = parent.get("database_id")
            return self._parent_database_id
            
        return None
    
    async def is_database_page(self) -> bool:
        """
        Checks if this page belongs to a database.
        
        Returns:
            bool: True if the page belongs to a database, False otherwise
        """
        database_id = await self.get_parent_database_id()
        return database_id is not None
        
    async def get_database_schema(self) -> Dict[str, Any]:
        """
        Gets the schema of the database this page belongs to, if any.
        
        Returns:
            Dict[str, Any]: The database schema or an empty dict if the page doesn't belong to a database
        """
        if self._database_schema is not None:
            return self._database_schema
            
        database_id = await self.get_parent_database_id()
        if not database_id:
            return {}
            
        try:
            database = await self._client.get(f"databases/{database_id}")
            if database and "properties" in database:
                self._database_schema = database["properties"]
                return self._database_schema
        except Exception as e:
            self.logger.error("Error getting database schema: %s", str(e))
            
        return {}
    
    async def get_property_schema(self, property_name: str) -> Optional[Dict[str, Any]]:
        """
        Gets the schema for a specific property.
        
        Args:
            property_name: The name of the property
            
        Returns:
            Optional[Dict[str, Any]]: The property schema or None if not found
        """
        schema = await self.get_database_schema()
        
        if not schema or property_name not in schema:
            return None
            
        return schema[property_name]
    
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
    
    async def get_available_option_names(self, property_name: str) -> List[str]:
        """
        Gets the available option names for a property (select, multi_select, status).
        
        Args:
            property_name: The name of the property
            
        Returns:
            List[str]: List of available option names
        """
        options = await self.get_property_options(property_name)
        return [option.get("name", "") for option in options]
    
    async def get_all_property_types(self) -> Dict[str, str]:
        """
        Gets all property types for the database.
        
        Returns:
            Dict[str, str]: Dictionary mapping property names to their types
        """
        schema = await self.get_database_schema()
        
        if not schema:
            return {}
            
        return {
            prop_name: prop_data.get("type", "unknown")
            for prop_name, prop_data in schema.items()
        }
    
    async def get_database_metadata(self, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Gets the complete metadata of the database, including property options.
        
        Args:
            include_types: List of property types to include (if None, include all)
            
        Returns:
            Dict[str, Any]: The database metadata
        """
        schema = await self.get_database_schema()
        
        if not schema:
            return {"properties": {}}
            
        metadata = {"properties": {}}
        
        for prop_name, prop_data in schema.items():
            prop_type = prop_data.get("type")
            
            if include_types and prop_type not in include_types:
                continue
                
            prop_metadata = {
                "type": prop_type,
                "options": []
            }
            
            # Include options for select, multi_select, status
            if prop_type in ["select", "multi_select", "status"]:
                prop_metadata["options"] = prop_data.get(prop_type, {}).get("options", [])
                
            metadata["properties"][prop_name] = prop_metadata
            
        return metadata