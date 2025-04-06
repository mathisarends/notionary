import re
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

    def __init__(
        self,
        page_id: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        if not page_id and not url:
            raise ValueError("Entweder page_id oder url muss angegeben werden")

        if not page_id and url:
            page_id = self._extract_notion_uuid(url)
            if not page_id:
                raise ValueError(
                    f"Konnte keine gültige UUID aus der URL extrahieren: {url}"
                )

        if not self._validate_uuid_format(page_id):
            parsed_id = self._extract_notion_uuid(page_id)
            if not parsed_id:
                raise ValueError(
                    f"Ungültiges UUID-Format und konnte nicht geparst werden: {page_id}"
                )
            page_id = parsed_id

        print("page_id:", page_id)
        input("Drücke enter um weiterzumachen")

        self.page_id = page_id
        self.url = url

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

    @staticmethod
    def _extract_notion_uuid(url: str) -> Optional[str]:
        uuid_pattern = r"([a-f0-9]{32})"
        match = re.search(uuid_pattern, url.lower())

        if not match:
            return None

        uuid_raw = match.group(1)

        formatted_uuid = f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"

        return formatted_uuid

    @staticmethod
    def _validate_uuid_format(uuid: str) -> bool:
        uuid_pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
        return bool(re.match(uuid_pattern, uuid.lower()))
