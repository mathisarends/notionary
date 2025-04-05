import asyncio
import json
from typing import Any, Dict, Optional, TypedDict
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class PageMetadata(TypedDict, total=False):
    """Type definition for page metadata."""
    id: str
    title: str
    icon: Optional[Dict[str, Any]]
    cover: Optional[Dict[str, Any]]
    parent: Dict[str, Any]
    url: str
    created_time: str
    last_edited_time: str
    created_by: Dict[str, Any]
    last_edited_by: Dict[str, Any]
    properties: Dict[str, Any]


class NotionPageMetadataManager(LoggingMixin):
    """Class for retrieving and managing Notion page metadata."""
    
    # Default Notion cover image to use when none is specified
    DEFAULT_COVER_URL = "https://www.notion.so/images/page-cover/gradients_3.png"
    
    def __init__(self, page_id: str, token: Optional[str] = None):
        self._client = NotionClient(token=token)
        self.page_id = page_id
    
    async def get_page_metadata(self, page_id: Optional[str] = None) -> Optional[PageMetadata]:
        """
        Retrieves metadata for a specific Notion page.
        
        Args:
            page_id: Optional page ID (if None, uses the ID from initialization)
            
        Returns:
            PageMetadata dictionary if successful, None if error occurs
        """
        page_id = page_id or self.page_id
            
        result = await self._client.get(f"pages/{page_id}")
        
        if not result:
            self.logger.error("Error retrieving page metadata: %s", result.error)
            return None
        
        page_data = result.data
        
        title = ""
        if "properties" in page_data and "title" in page_data["properties"]:
            title_property = page_data["properties"]["title"]
            if "title" in title_property and title_property["title"]:
                title = "".join([text_item.get("plain_text", "") for text_item in title_property["title"]])
        
        metadata: PageMetadata = {
            "id": page_data.get("id", ""),
            "title": title,
            "icon": page_data.get("icon"),
            "cover": page_data.get("cover"),
            "parent": page_data.get("parent", {}),
            "url": page_data.get("url", ""),
            "created_time": page_data.get("created_time", ""),
            "last_edited_time": page_data.get("last_edited_time", ""),
            "created_by": page_data.get("created_by", {}),
            "last_edited_by": page_data.get("last_edited_by", {}),
            "properties": page_data.get("properties", {})
        }
        
        return metadata
    
    async def get_database_metadata(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata for a specific Notion database.
        
        Args:
            database_id: The ID of the Notion database
            
        Returns:
            Database metadata dictionary if successful, None if error occurs
        """
        result = await self._client.get(f"databases/{database_id}")
        
        if not result:
            self.logger.error("Error retrieving database metadata: %s", result.error)
            return None
        
        return result.data
    
    async def get_parent_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata for the parent of a specific Notion page.
        """
        page_metadata = await self.get_page_metadata(self.page_id)
        
        if not page_metadata or "parent" not in page_metadata:
            return None
        
        parent = page_metadata["parent"]
        parent_type = list(parent.keys())[0] if parent else None
        parent_id = parent.get(parent_type) if parent_type else None
        
        if not parent_id:
            return None
        
        if parent_type == "database_id":
            return await self.get_database_metadata(parent_id)
        if parent_type == "page_id":
            return await self.get_page_metadata(parent_id)
        
        return {"type": parent_type, "id": parent_id}
    
    async def set_page_icon(self, emoji: Optional[str] = None, 
                          external_url: Optional[str] = None) -> Optional[PageMetadata]:
        """
        Sets the icon for a Notion page (either emoji or external image).
        """
        if not emoji and not external_url:
            self.logger.error("Either emoji or external_url must be provided")
            return None
        
        if emoji:
            icon = {"type": "emoji", "emoji": emoji}
        else:
            icon = {"type": "external", "external": {"url": external_url}}
        
        result = await self._client.patch(f"pages/{self.page_id}", {"icon": icon})
        
        if not result:
            self.logger.error("Error setting page icon: %s", result.error)
            return None
        
        return await self.get_page_metadata(self.page_id)
    
    async def set_page_cover(self, 
                           external_url: Optional[str] = None) -> Optional[PageMetadata]:
        """
        Sets the cover image for a Notion page.
        """
        url_to_use = external_url or self.DEFAULT_COVER_URL
        
        cover = {"type": "external", "external": {"url": url_to_use}}
        result = await self._client.patch(f"pages/{self.page_id}", {"cover": cover})
        
        if not result:
            self.logger.error("Error setting page cover: %s", result.error)
            return None
        
        return await self.get_page_metadata(self.page_id)
    
    

async def run_demo():
    soundcore_page_id = "1c8389d5-7bd3-814a-974e-f9e706569b16"
    
    manager = NotionPageMetadataManager(page_id=soundcore_page_id)
    
    print("Aktuelle Seiten-Metadaten:")
    metadata = await manager.get_page_metadata()
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    # print("\nSetze ein Emoji-Icon (Lautsprecher)...")
    # await manager.set_page_icon(emoji="🔊")
    
    # print("\nSetze ein Cover-Bild...")
    # cover_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    # await manager.set_page_cover(external_url=cover_url)
    
    # # 4. Zeige die aktualisierten Metadaten an
    # print("\nAktualisierte Seiten-Metadaten:")
    # updated_metadata = await manager.get_page_metadata()
    # if updated_metadata:
    #     print(f"Titel: {updated_metadata['title']}")
    #     print(f"Icon: {updated_metadata.get('icon')}")
    #     print(f"Cover: {updated_metadata.get('cover')}")


# Führe die Demo aus
if __name__ == "__main__":
    asyncio.run(run_demo())