from typing import Any, Dict, List, Optional, Union
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)
from notionary.core.converters.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.core.notion_client import NotionClient
from notionary.core.page.page_content_manager import PageContentManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.core.page.meta_data.metadata_editor import MetadataEditor
from notionary.util.uuid_utils import extract_uuid, format_uuid, is_valid_uuid


class NotionPageManager(LoggingMixin):
    """
    High-Level Fassade zur Verwaltung von Inhalten und Metadaten einer Notion-Seite.
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

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_standard_registry()
        )

        self._page_content_manager = PageContentManager(
            page_id=page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )
        self._metadata = MetadataEditor(page_id, self._client)

    @property
    def page_id(self) -> Optional[str]:
        """Get the title of the page."""
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

    async def get_blocks(self) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_blocks()

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_block_children(block_id)

    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        return await self._page_content_manager.get_page_blocks_with_children()

    async def get_text(self) -> str:
        return await self._page_content_manager.get_text()

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_title(title)

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_icon(emoji, external_url)
    
    async def get_icon(self) -> Optional[str]:
        """
        Retrieves the page icon - either emoji or external URL.
        
        Returns:
            str: Emoji character or URL if set, None if no icon
        """
        page_data = await self._client.get_page(self._page_id)
        
        if not page_data or "icon" not in page_data:
            return None
        
        icon_data = page_data.get("icon", {})
        icon_type = icon_data.get("type")
        
        if icon_type == "emoji":
            return icon_data.get("emoji")
        elif icon_type == "external":
            return icon_data.get("external", {}).get("url")
        
        return None  

    
    async def get_cover_url(self) -> str:
        page_data = await self._client.get_page(self._page_id)
        
        if not page_data:
            return ""
        
        return page_data.get("cover", {}).get("external", {}).get("url", "")

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_cover(external_url)
    
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_random_gradient_cover()
    
    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page"""
        page_data = await self._client.get_page(self._page_id)
        if page_data and "properties" in page_data:
            return page_data["properties"]
        return {}

    async def get_status(self) -> Optional[str]:
        """
        Determines the status of the page (e.g., 'Draft', 'Completed', etc.)
        
        Returns:
            Optional[str]: The status as a string or None if not available
        """
        properties = await self.get_properties()
        if "Status" in properties and properties["Status"].get("status"):
            return properties["Status"]["status"]["name"]
        return None
    
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
    
    # Aufjedenfall auslagern
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
        
        Args:
            property_name: The name of the property
            value: The value to set
            
        Returns:
            Optional[Dict[str, Any]]: The API response or None if it fails
        """
        return await self._metadata.set_property_by_name(property_name, value)
    
    
async def main(): 
    page_manager = NotionPageManager(page_id="https://notion.so/1d0389d57bd3805cb34ccaf5804b43ce")
    await page_manager.set_property_by_name("Projekte", "Smart Home")
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
