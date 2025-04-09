import asyncio
from typing import Any, Dict, List, Optional, Union
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)
from notionary.core.converters.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.core.notion_client import NotionClient
from notionary.core.page.database_property_service import DatabasePropertyService
from notionary.core.page.meta_data.notion_icon_manager import NotionPageIconManager
from notionary.core.page.meta_data.notion_page_cover_manager import NotionPageCoverManager
from notionary.core.page.page_content_manager import PageContentManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.core.page.meta_data.metadata_editor import MetadataEditor
from notionary.util.uuid_utils import extract_uuid, format_uuid, is_valid_uuid
from notionary.core.page.page_database_relation import PageDatabaseRelation


# TODO: Für diese Validierungslogik kann man eigentlich auch eine Oberklasse einführen weil das ist ja wirklich fest.
class NotionPageManager(LoggingMixin):
    """
    High-Level Facade for managing content and metadata of a Notion page.
    """

    def __init__(
        self,
        page_id: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        if not page_id and not url:
            raise ValueError("Either page_id or url must be provided")

        if not page_id and url:
            page_id = extract_uuid(url)
            if not page_id:
                raise ValueError(f"Could not extract a valid UUID from the URL: {url}")

        page_id = format_uuid(page_id)
        if not page_id or not is_valid_uuid(page_id):
            raise ValueError(f"Invalid UUID format: {page_id}")

        self._page_id = page_id
        self.url = url
        self._title = title
        self._client = NotionClient(token=token)
        self._page_data = None

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_standard_registry()
        )

        self._page_content_manager = PageContentManager(
            page_id=page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )
        self._metadata = MetadataEditor(page_id, self._client)
        self._page_cover_manager = NotionPageCoverManager(page_id=page_id, client=self._client)
        self._page_icon_manager = NotionPageIconManager(page_id=page_id, client=self._client)
        
        self._db_relation = PageDatabaseRelation(page_id, self._client)
        self._db_property_service = None  # Will be lazily initialized if needed

    async def _init_db_property_service(self) -> Optional[DatabasePropertyService]:
        """
        Lazily initializes the database property service if the page belongs to a database.
        
        Returns:
            Optional[DatabasePropertyService]: The initialized service or None
        """
        if self._db_property_service is not None:
            return self._db_property_service
            
        database_id = await self._db_relation.get_parent_database_id()
        if database_id:
            self._db_property_service = DatabasePropertyService(database_id, self._client)
            await self._db_property_service.load_schema()
            return self._db_property_service
            
        return None

    @property
    def page_id(self) -> Optional[str]:
        """Get the ID of the page."""
        return self._page_id

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def block_registry(self) -> BlockElementRegistry:
        return self._block_element_registry

    @block_registry.setter
    def block_registry(self, block_registry: BlockElementRegistry) -> None:
        """Set the block element registry for the page content manager."""
        self._block_element_registry = block_registry
        self._page_content_manager = PageContentManager(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )

    # Content management methods
    
    async def append_markdown(self, markdown: str) -> str:
        return await self._page_content_manager.append_markdown(markdown)

    async def clear(self) -> str:
        return await self._page_content_manager.clear()

    async def replace_content(self, markdown: str) -> str:
        await self._page_content_manager.clear()
        return await self._page_content_manager.append_markdown(markdown)

    async def get_blocks(self) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_blocks()

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_block_children(block_id)

    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_page_blocks_with_children()

    async def get_text(self) -> str:
        return await self._page_content_manager.get_text()
    
    # Basic metadata methods

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_title(title)

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._page_icon_manager.set_icon(emoji, external_url)
    
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
    
    async def get_icon(self) -> Optional[str]:
        """
        Retrieves the page icon - either emoji or external URL.
        
        Returns:
            str: Emoji character or URL if set, None if no icon
        """
        return await self._page_icon_manager.get_icon()

    async def get_cover_url(self) -> str:
        return await self._page_cover_manager.get_cover_url()

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_cover(external_url)
    
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_random_gradient_cover()
    
    # Property methods
    
    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page"""
        page_data = await self._get_page_data()
        if page_data and "properties" in page_data:
            return page_data["properties"]
        return {}

    async def get_property_value(self, property_name: str) -> Any:
        """
        Get the value of a specific property.
        
        Args:
            property_name: The name of the property
            
        Returns:
            Any: The value of the property, or None if not found
        """
        properties = await self.get_properties()
        if property_name not in properties:
            return None
            
        prop_data = properties[property_name]
        prop_type = prop_data.get("type")
        
        if not prop_type:
            return None
            
        # Extract the value based on property type
        if prop_type == "title" and "title" in prop_data:
            return "".join([text_obj.get("plain_text", "") for text_obj in prop_data["title"]])
        elif prop_type == "rich_text" and "rich_text" in prop_data:
            return "".join([text_obj.get("plain_text", "") for text_obj in prop_data["rich_text"]])
        elif prop_type == "number" and "number" in prop_data:
            return prop_data["number"]
        elif prop_type == "select" and "select" in prop_data and prop_data["select"]:
            return prop_data["select"].get("name")
        elif prop_type == "multi_select" and "multi_select" in prop_data:
            return [option.get("name") for option in prop_data["multi_select"]]
        elif prop_type == "status" and "status" in prop_data and prop_data["status"]:
            return prop_data["status"].get("name")
        elif prop_type == "date" and "date" in prop_data and prop_data["date"]:
            return prop_data["date"]
        elif prop_type == "checkbox" and "checkbox" in prop_data:
            return prop_data["checkbox"]
        elif prop_type == "url" and "url" in prop_data:
            return prop_data["url"]
        elif prop_type == "email" and "email" in prop_data:
            return prop_data["email"]
        elif prop_type == "phone_number" and "phone_number" in prop_data:
            return prop_data["phone_number"]
        elif prop_type == "relation" and "relation" in prop_data:
            return [rel.get("id") for rel in prop_data["relation"]]
        elif prop_type == "people" and "people" in prop_data:
            return [person.get("id") for person in prop_data["people"]]
        elif prop_type == "files" and "files" in prop_data:
            return [
                file.get("external", {}).get("url") 
                if file.get("type") == "external" else file.get("name") 
                for file in prop_data["files"]
            ]
            
        return None
    
    async def set_property_by_name(self, property_name: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Set a property value by name, automatically detecting the property type.
        Includes validation against database schema for select/multi_select/status properties.
        
        Args:
            property_name: The name of the property
            value: The value to set
            
        Returns:
            Optional[Dict[str, Any]]: The API response or None if it fails
        """
        # If the page belongs to a database, validate the value against the database schema
        if await self.is_database_page():
            db_service = await self._init_db_property_service()
            if db_service:
                # Validate the value
                is_valid, error_message, available_options = await db_service.validate_property_value(
                    property_name, value
                )
                
                if not is_valid:
                    self.logger.warning(error_message)
                    
                    if available_options:
                        options_str = ", ".join(f"'{option}'" for option in available_options)
                        self.logger.info(f"Available options for '{property_name}': {options_str}")
                        
                    return None
        
        return await self._metadata.set_property_by_name(property_name, value)
        
    # Database relation methods (delegated to PageDatabaseRelation)
    
    async def is_database_page(self) -> bool:
            """
            Checks if this page belongs to a database.
            
            Returns:
                bool: True if the page belongs to a database, False otherwise
            """
            return await self._db_relation.is_database_page()
        
    async def get_parent_database_id(self) -> Optional[str]:
        """
        Gets the ID of the database this page belongs to, if any.
        
        Returns:
            Optional[str]: The database ID or None if the page doesn't belong to a database
        """
        return await self._db_relation.get_parent_database_id()

    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """
        Gets the available option names for a property (select, multi_select, status).
        
        Args:
            property_name: The name of the property
            
        Returns:
            List[str]: List of available option names
        """
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """
        Gets the type of a specific property.
        
        Args:
            property_name: The name of the property
            
        Returns:
            Optional[str]: The property type or None if not found
        """
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def get_database_metadata(self, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Gets complete metadata about the database this page belongs to.
        
        Args:
            include_types: List of property types to include (if None, include all)
            
        Returns:
            Dict[str, Any]: Database metadata including property types and options
        """
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_database_metadata(include_types)
        return {"properties": {}}

    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Gets available options for a relation property.
        
        Args:
            property_name: The name of the relation property
            limit: Maximum number of options to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of relation options with ID and name
        """
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_relation_options(property_name, limit)
        return []

    async def add_relation(self, relation_property_name: str, page_ids: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        Add a relation to another page or pages.
        
        Args:
            relation_property_name: The name of the relation property
            page_ids: A single page ID or list of page IDs to relate to
            
        Returns:
            Optional[Dict[str, Any]]: The API response or None if it fails
        """
        existing_relations = await self.get_property_value(relation_property_name) or []
        
        if isinstance(page_ids, str):
            page_ids = [page_ids]
            
        # Combine existing and new relations, removing duplicates
        all_relations = list(set(existing_relations + page_ids))
        
        return await self.set_property_by_name(relation_property_name, all_relations)

    async def get_status(self) -> Optional[str]:
        """
        Determines the status of the page (e.g., 'Draft', 'Completed', etc.)
        
        Returns:
            Optional[str]: The status as a string or None if not available
        """
        return await self.get_property_value("Status")
        
async def main():
    """
    Demonstriert die Verwendung des refactorierten NotionPageManager.
    """
    print("=== NotionPageManager Demo ===")
    
    page_manager = NotionPageManager(page_id="https://notion.so/1d0389d57bd3805cb34ccaf5804b43ce")
    
    is_database_page = await page_manager.is_database_page()
    print(f"\n1. Ist diese Seite Teil einer Datenbank? {is_database_page}")
    
    if not is_database_page:
        print("Diese Seite gehört zu keiner Datenbank. Demo wird beendet.")
        return
        
    db_id = await page_manager.get_parent_database_id()
    print(f"\n2. Datenbank-ID: {db_id}")
    
    properties = await page_manager.get_properties()
    print("\n3. Aktuelle Eigenschaften der Seite:")
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type", "unbekannt")
        
        # Wert für jede Eigenschaft extrahieren und anzeigen
        value = await page_manager.get_property_value(prop_name)
        print(f"  - {prop_name} ({prop_type}): {value}")
    
    # 4. Verfügbare Status-Optionen anzeigen
    status_options = await page_manager.get_available_options_for_property("Status")
    print(f"\n4. Verfügbare Status-Optionen: {status_options}")
    
    # 5. Verfügbare Tags (Multi-Select) anzeigen
    tags_options = await page_manager.get_available_options_for_property("Tags")
    print(f"\n5. Verfügbare Tags-Optionen: {tags_options}")
    
    # 6. Verfügbare Optionen für alle Relationen anzeigen
    print("\n6. Relation-Eigenschaften und deren Optionen:")
    for prop_name, prop_data in properties.items():
        if prop_data.get("type") == "relation":
            relation_options = await page_manager.get_relation_options(prop_name, limit=5)
            option_names = [option.get("name", "Unbenannt") for option in relation_options]
            print(f"  - {prop_name} Relation-Optionen (max. 5): {option_names}")
    
    # 7. Typ für jede Eigenschaft abfragen
    print("\n7. Typen aller Eigenschaften:")
    for prop_name in properties.keys():
        prop_type = await page_manager.get_property_type(prop_name)
        print(f"  - {prop_name}: {prop_type}")
    
    # 8. Einen gültigen Status setzen (erste verfügbare Option)
    if status_options:
        valid_status = status_options[0]
        print(f"\n8. Setze Status auf '{valid_status}'...")
        result = await page_manager.set_property_by_name("Status", valid_status)
        print(f"   Ergebnis: {'Erfolgreich' if result else 'Fehlgeschlagen'}")
        
        # Aktuellen Status nach der Änderung anzeigen
        current_status = await page_manager.get_status()
        print(f"   Aktueller Status: {current_status}")
    
    # 9. Versuch, einen ungültigen Status zu setzen
    invalid_status = "Bin King"
    print(f"\n9. Versuche ungültigen Status '{invalid_status}' zu setzen...")
    result = await page_manager.set_property_by_name("Status", invalid_status)
    print(f"   Ergebnis: {'Erfolgreich' if result else 'Fehlgeschlagen'}")
    
    # 10. Komplette Datenbank-Metadaten für select-ähnliche Properties abrufen
    print("\n10. Datenbank-Metadaten für select, multi_select und status Properties:")
    metadata = await page_manager.get_database_metadata(
        include_types=["select", "multi_select", "status"]
    )
    
    for prop_name, prop_info in metadata.get("properties", {}).items():
        option_names = [opt.get("name", "") for opt in prop_info.get("options", [])]
        print(f"  - {prop_name} ({prop_info.get('type')}): {option_names}")
    
    print("\nDemonstration abgeschlossen.")


if __name__ == "__main__":
    asyncio.run(main())
