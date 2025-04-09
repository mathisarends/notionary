from typing import Any, Dict, List, Optional
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
    
    
async def main(): 
    page_manager = NotionPageManager(page_id="https://notion.so/1d0389d57bd3805cb34ccaf5804b43ce")
    icon = await page_manager.get_icon()
    print(f"Cover URL: {icon}")
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
