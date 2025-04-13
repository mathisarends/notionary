import asyncio
from typing import Any, Dict, List, Optional, Union
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)
from notionary.core.converters.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.core.notion_client import NotionClient
from notionary.core.page.metadata.metadata_editor import MetadataEditor
from notionary.core.page.metadata.notion_icon_manager import NotionPageIconManager
from notionary.core.page.metadata.notion_page_cover_manager import NotionPageCoverManager
from notionary.core.page.properites.database_property_service import DatabasePropertyService
from notionary.core.page.relations.notion_page_relation_manager import NotionRelationManager
from notionary.core.page.content.page_content_manager import PageContentManager
from notionary.core.page.properites.page_property_manager import PagePropertyManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import extract_and_validate_page_id
from notionary.core.page.relations.page_database_relation import PageDatabaseRelation

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
        self._page_id = extract_and_validate_page_id(page_id=page_id, url=url)

        self.url = url
        self._title = title
        self._client = NotionClient(token=token)
        self._page_data = None

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_standard_registry()
        )

        self._page_content_manager = PageContentManager(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )
        self._metadata = MetadataEditor(self._page_id, self._client)
        self._page_cover_manager = NotionPageCoverManager(page_id=self._page_id, client=self._client)
        self._page_icon_manager = NotionPageIconManager(page_id=self._page_id, client=self._client)
        
        self._db_relation = PageDatabaseRelation(page_id=self._page_id, client=self._client)
        self._db_property_service = None
        
        self._relation_manager = NotionRelationManager(page_id=self._page_id, client=self._client)
        
        self._property_manager = PagePropertyManager(
            self._page_id, 
            self._client,
            self._metadata,
            self._db_relation
        )

    async def _get_db_property_service(self) -> Optional[DatabasePropertyService]:
        """
        Gets the database property service, initializing it if necessary.
        This is a more intuitive way to work with the instance variable.
        
        Returns:
            Optional[DatabasePropertyService]: The database property service or None if not applicable
        """
        if self._db_property_service is not None:
            return self._db_property_service
            
        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None
        
        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service

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

    async def append_markdown(self, markdown: str) -> str:
        return await self._page_content_manager.append_markdown(markdown)

    async def clear(self) -> str:
        return await self._page_content_manager.clear()

    async def replace_content(self, markdown: str) -> str:
        await self._page_content_manager.clear()
        return await self._page_content_manager.append_markdown(markdown)

    async def get_text(self) -> str:
        return await self._page_content_manager.get_text()
    
    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_title(title)

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._page_icon_manager.set_icon(emoji, external_url)
    
    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
        """ Gets the page data and caches it for future use.
        """
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data
    
    async def get_icon(self) -> Optional[str]:
        """Retrieves the page icon - either emoji or external URL.
        """
        return await self._page_icon_manager.get_icon()

    async def get_cover_url(self) -> str:
        return await self._page_cover_manager.get_cover_url()

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_cover(external_url)
    
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        return await self._page_cover_manager.set_random_gradient_cover()
    
    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page."""
        return await self._property_manager.get_properties()

    async def get_property_value(self, property_name: str) -> Any:
        """Get the value of a specific property."""
        return await self._property_manager.get_property_value(
            property_name, 
            self._relation_manager.get_relation_values
        )
    
    async def set_property_by_name(self, property_name: str, value: Any) -> Optional[Dict[str, Any]]:
        """ Sets the value of a specific property by its name.
        """ 
        return await self._property_manager.set_property_by_name(
            property_name=property_name, 
            value=value,
        )
        
    async def is_database_page(self) -> bool:
        """ Checks if this page belongs to a database.
        """
        return await self._db_relation.is_database_page()
        
    async def get_parent_database_id(self) -> Optional[str]:
        """ Gets the ID of the database this page belongs to, if any
        """
        return await self._db_relation.get_parent_database_id()

    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """ Gets the available option names for a property (select, multi_select, status).
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """ Gets the type of a specific property.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def get_database_metadata(self, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """ Gets complete metadata about the database this page belongs to.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_database_metadata(include_types)
        return {"properties": {}}

    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, Any]]:
            """ Returns available options for a relation property.
            """
            return await self._relation_manager.get_relation_options(property_name, limit)

    async def add_relations_by_name(self, relation_property_name: str, page_titles: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """ Adds one or more relations.
        """
        return await self._relation_manager.add_relation_by_name(property_name=relation_property_name, page_titles=page_titles)

    async def get_relation_values(self, property_name: str) -> List[str]:
        """
        Returns the current relation values for a property.
        """
        return await self._relation_manager.get_relation_values(property_name)

    async def get_relation_property_ids(self) -> List[str]:
        """ Returns a list of all relation property names.
        """
        return await self._relation_manager.get_relation_property_ids()

    async def get_all_relations(self) -> Dict[str, List[str]]:
        """ Returns all relation properties and their values.
        """
        return await self._relation_manager.get_all_relations()
        
    async def get_status(self) -> Optional[str]:
        """ Determines the status of the page (e.g., 'Draft', 'Completed', etc.)
        """
        return await self.get_property_value("Status")
    
    
    
async def main():
    """
    Demonstriert die Verwendung des refactorierten NotionPageManager.
    """
    print("=== NotionPageManager Demo ===")
    
    page_manager = NotionPageManager(page_id="https://notion.so/1d0389d57bd3805cb34ccaf5804b43ce")
    
    await page_manager.add_relations_by_name("Projekte", ["Fetzen mit Stine"])


    input("Drücke Enter, um fortzufahren...")

    
    is_database_page = await page_manager.is_database_page()
    
    if not is_database_page:
        print("Diese Seite gehört zu keiner Datenbank. Demo wird beendet.")
        return
        
    db_id = await page_manager.get_parent_database_id()
    print(f"\n2. Datenbank-ID: {db_id}")
    
    properties = await page_manager.get_properties()
    print("\n3. Aktuelle Eigenschaften der Seite:")
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type", "unbekannt")
        
        value = await page_manager.get_property_value(prop_name)
        print(f"  - {prop_name} ({prop_type}): {value}")
    
    status_options = await page_manager.get_available_options_for_property("Status")
    print(f"\n4. Verfügbare Status-Optionen: {status_options}")
    
    tags_options = await page_manager.get_available_options_for_property("Tags")
    print(f"\n5. Verfügbare Tags-Optionen: {tags_options}")
    
    print("\n6. Relation-Eigenschaften und deren Optionen:")
    for prop_name, prop_data in properties.items():
        if prop_data.get("type") == "relation":
            relation_options = await page_manager.get_relation_options(prop_name, limit=5)
            option_names = [option.get("name", "Unbenannt") for option in relation_options]
            print(f"  - {prop_name} Relation-Optionen (max. 5): {option_names}")
    
    print("\n7. Typen aller Eigenschaften:")
    for prop_name in properties.keys():
        prop_type = await page_manager.get_property_type(prop_name)
        print(f"  - {prop_name}: {prop_type}")
    
    if status_options:
        valid_status = status_options[0]
        print(f"\n8. Setze Status auf '{valid_status}'...")
        result = await page_manager.set_property_by_name("Status", valid_status)
        print(f"   Ergebnis: {'Erfolgreich' if result else 'Fehlgeschlagen'}")
        
        current_status = await page_manager.get_status()
        print(f"   Aktueller Status: {current_status}")
    
    # 9. Versuch, einen ungültigen Status zu setzen
    invalid_status = "Bin King"
    print(f"\n9. Versuche ungültigen Status '{invalid_status}' zu setzen...")
    await page_manager.set_property_by_name("Status", invalid_status)
    
    # 10. Komplette Datenbank-Metadaten für select-ähnliche Properties abrufen
    print("\n10. Datenbank-Metadaten für select, multi_select und status Properties:")
    metadata = await page_manager.get_database_metadata(
        include_types=["select", "multi_select", "status"]
    )
    
    for prop_name, prop_info in metadata.get("properties", {}).items():
        option_names = [opt.get("name", "") for opt in prop_info.get("options", [])]
        print(f"  - {prop_name} ({prop_info.get('type')}): {option_names}")
    
    print("\nDemonstration abgeschlossen.")


async def demo2():
    url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"
    
    page_manager = NotionPageManager(url=url)
    
    # Beispiel mit einem Embed-Element im Transcript-Toggle
    markdown = """
## 💪 Muskelaufbau und Kraft
- Regelmäßiges Training ist essentiell für den Muskelerhalt im Alter
- Richtige Ernährung unterstützt die Regeneration nach dem Training

+++ Transcript
    <embed:Listen to this highlight>(https://share.snipd.com/snip/ad3d95b2-d648-4fa9-9036-bd7df653ea32)
    <!-- spacer -->
    ... In diesem Teil des Podcasts erklärt der Sprecher, wie das Henneman-Größenprinzip funktioniert und wie Muskelfasern rekrutiert werden, basierend auf der Schwere des zu bewegenden Objekts.
"""
    
    await page_manager.append_markdown(markdown)
    print("Markdown wurde zur Notion-Seite hinzugefügt.")

if __name__ == "__main__":
    asyncio.run(demo2())
    print("\nDemonstration completed.")