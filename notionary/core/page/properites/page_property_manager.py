from typing import Dict, Any, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.metadata.metadata_editor import MetadataEditor
from notionary.core.page.relations.notion_page_title_resolver import NotionPageTitleResolver
from notionary.core.page.properites.database_property_service import DatabasePropertyService
from notionary.core.page.relations.page_database_relation import PageDatabaseRelation
from notionary.core.page.properites.property_value_extractor import PropertyValueExtractor
from notionary.util.logging_mixin import LoggingMixin


class PagePropertyManager(LoggingMixin):
    """Verwaltet den Zugriff auf und die Änderung von Seiteneigenschaften."""
    
    def __init__(self, page_id: str, client: NotionClient, 
                metadata_editor: MetadataEditor, 
                db_relation: PageDatabaseRelation):
        self._page_id = page_id
        self._client = client
        self._page_data = None
        self._metadata_editor = metadata_editor
        self._db_relation = db_relation
        self._db_property_service = None
        
        self._extractor = PropertyValueExtractor(self.logger)
        self._title_resolver = NotionPageTitleResolver(client)
    
    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page."""
        page_data = await self._get_page_data()
        if page_data and "properties" in page_data:
            return page_data["properties"]
        return {}
    
    async def get_property_value(self, property_name: str, relation_getter=None) -> Any:
        """
        Get the value of a specific property.
        
        Args:
            property_name: Name of the property to get
            relation_getter: Optional callback function to get relation values
        """
        properties = await self.get_properties()
        if property_name not in properties:
            return None
            
        prop_data = properties[property_name]
        return await self._extractor.extract(property_name, prop_data, relation_getter)
    
    async def set_property_by_name(self, property_name: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Set a property value by name, automatically detecting the property type.
        
        Args:
            property_name: Name der Eigenschaft
            value: Zu setzender Wert
            
        Returns:
            Optional[Dict[str, Any]]: API-Antwort oder None bei Fehler
        """
        property_type = await self.get_property_type(property_name)
        
        if property_type == "relation":
            self.logger.warning(
                "Property '%s' ist vom Typ 'relation'. Relationen müssen über den "
                "RelationManager gesetzt werden, z.B. mit add_relation_by_name().", 
                property_name
            )
            return None
        
        # Normale Eigenschaftsbehandlung fortsetzen
        if not await self._db_relation.is_database_page():
            result = await self._metadata_editor.set_property_by_name(property_name, value)
            if result:
                await self.invalidate_cache()
            return result
        
        db_service = await self._init_db_property_service()
        
        if not db_service:
            result = await self._metadata_editor.set_property_by_name(property_name, value)
            if result:
                await self.invalidate_cache()
            return result
        
        is_valid, error_message, available_options = await db_service.validate_property_value(
            property_name, value
        )
                
        if not is_valid:
            self.logger.warning(error_message)
                    
            if not available_options:
                self.logger.warning("No valid options available for '%s'", property_name)
                return None
            
            options_str = ", ".join(f"'{option}'" for option in available_options)
            self.logger.info("Available options for '%s': %s", property_name, options_str)
            return None
            
        result = await self._metadata_editor.set_property_by_name(property_name, value)
        if result:
            await self.invalidate_cache()
        return result
    
    async def get_property_type(self, property_name: str) -> Optional[str]:
        """Gets the type of a specific property."""
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None
    
    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """Gets the available option names for a property."""
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []
    
    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
        """Gets the page data and caches it for future use."""
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data
    
    async def invalidate_cache(self) -> None:
        """Forces a refresh of the cached page data on next access."""
        self._page_data = None
        
    async def _init_db_property_service(self) -> Optional[DatabasePropertyService]:
        """Lazily initializes the database property service if needed."""
        if self._db_property_service is not None:
            return self._db_property_service
            
        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None
        
        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service