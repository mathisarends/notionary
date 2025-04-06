from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.meta_data.metadata_cache import MetadataCache
from notionary.core.page.meta_data.metadata_property_manager import MetadataPropertManager
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin

class PageMetadataProvider(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client
        self._cache = MetadataCache(client)
        self._formatter = NotionPropertyFormatter()
        self._properties = MetadataPropertManager(client, self._cache, self._formatter)

    async def get_page_metadata(self) -> Optional[Dict[str, Any]]:
        cached = self._cache.get_cached_metadata(self.page_id)
        if cached:
            return cached

        metadata = await self._client.api_get(f"pages/{self.page_id}")
        if not metadata:
            return None

        self._cache.set_cached_metadata(self.page_id, metadata)

        if "properties" in metadata and not self._cache.is_building_cache():
            await self._build_properties_cache(metadata["properties"])

        return metadata

    async def _build_properties_cache(self, properties: Dict[str, Any]) -> None:
        self._cache.set_building_cache(True)
        try:
            for name, prop_data in properties.items():
                prop_id = prop_data.get("id")
                prop_type = prop_data.get("type")
                self._cache.set_property_data(self.page_id, name, {
                    "id": prop_id,
                    "type": prop_type,
                    "data": prop_data.get(prop_type, {})
                })

            await self._load_status_options_if_needed()
        finally:
            self._cache.set_building_cache(False)

    async def _load_status_options_if_needed(self) -> None:
        metadata = self._cache.get_cached_metadata(self.page_id)
        if not metadata or "parent" not in metadata or "database_id" not in metadata["parent"]:
            return

        db_id = metadata["parent"]["database_id"]
        properties = self._cache.get_property_cache(self.page_id)
        status_props = [name for name, info in properties.items()
                        if info.get("type") == "status" and "options" not in info]

        if not status_props:
            return

        database_schema = await self._client.api_get(f"databases/{db_id}")
        if not database_schema or "properties" not in database_schema:
            return

        for prop_name in status_props:
            await self._add_status_options_to_property(prop_name, database_schema)

    async def _add_status_options_to_property(self, prop_name: str, database_schema: Dict[str, Any]) -> None:
        properties = self._cache.get_property_cache(self.page_id)
        if prop_name not in properties:
            return

        prop_info = properties[prop_name]
        prop_id = prop_info["id"]

        for db_prop_name, db_prop in database_schema["properties"].items():
            if db_prop.get("type") != "status" or db_prop.get("id") != prop_id:
                continue

            if "status" in db_prop and "options" in db_prop["status"]:
                prop_info["options"] = db_prop["status"]["options"]
                self._cache.set_property_data(self.page_id, prop_name, prop_info)
                break

    async def update_property_by_name(self, name: str, value: Any) -> Optional[Dict[str, Any]]:
        await self.get_page_metadata()
        return await self._properties.update_property(self.page_id, name, value)

    async def list_valid_status_options(self, name: str) -> List[str]:
        await self.get_page_metadata()
        return await self._properties.list_valid_status_options(self.page_id, name)

    async def find_property_by_type(self, prop_type: str) -> List[str]:
        await self.get_page_metadata()
        return await self._properties.find_property_by_type(self.page_id, prop_type)