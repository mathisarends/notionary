from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.meta_data.page_metadata_provider import PageMetadataProvider
from notionary.util.logging_mixin import LoggingMixin
from notionary.core.page.page_content import PageContentReader, PageContentEditor
from notionary.core.page.meta_data.metadata_editor import MetadataEditor

class NotionPageManager(LoggingMixin):
    """
    High-Level Fassade zur Verwaltung von Inhalten und Metadaten einer Notion-Seite.
    """

    def __init__(self, page_id: str, token: Optional[str] = None):
        self.page_id = page_id
        self._client = NotionClient(token=token)

        self._reader = PageContentReader(page_id, self._client)
        self._editor = PageContentEditor(page_id, self._client)
        self._metadata = MetadataEditor(page_id, self._client)
        self._provider = PageMetadataProvider(page_id, self._client)


    async def append_markdown(self, markdown: str) -> str:
        return await self._editor.append_markdown(markdown)

    async def clear(self) -> str:
        return await self._editor.clear()

    async def replace_content(self, markdown: str) -> str:
        return await self._editor.replace_content(markdown)

    async def get_blocks(self) -> List[Dict[str, Any]]:
        return await self._reader.get_blocks()

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        return await self._reader.get_block_children(block_id)

    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        return await self._reader.get_page_blocks_with_children()

    async def get_text(self) -> str:
        return await self._reader.get_text()
    
    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_title(title)

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_icon(emoji, external_url)

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        return await self._metadata.set_cover(external_url)

    async def get_metadata(self) -> Optional[Dict[str, Any]]:
        return await self._provider.get_page_metadata()

    async def update_property_by_name(
        self, name: str, value: Any
    ) -> Optional[Dict[str, Any]]:
        return await self._provider.update_property_by_name(name, value)

    async def list_valid_status_options(self, name: str) -> List[str]:
        return await self._provider.list_valid_status_options(name)

    async def close(self):
        await self._client.close()

