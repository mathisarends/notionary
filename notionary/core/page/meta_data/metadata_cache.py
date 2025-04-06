from typing import Any, Dict, Optional
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton_decorator import singleton


@singleton
class MetadataCache(LoggingMixin):
    """Verwaltet den Metadaten-Cache für Notion-Seiten."""

    def __init__(self, client: NotionClient):
        self._client = client
        self._page_metadata = {}
        self._property_cache = {}
        self._is_building_cache = False

    def get_cached_metadata(self, page_id: str) -> Optional[Dict[str, Any]]:
        return self._page_metadata.get(page_id)

    def set_cached_metadata(self, page_id: str, metadata: Dict[str, Any]) -> None:
        self._page_metadata[page_id] = metadata

    def clear_metadata(self, page_id: str) -> None:
        if page_id in self._page_metadata:
            del self._page_metadata[page_id]

    def get_property_cache(self, page_id: str) -> Dict[str, Any]:
        if page_id not in self._property_cache:
            self._property_cache[page_id] = {}
        return self._property_cache[page_id]

    def set_property_data(
        self, page_id: str, prop_name: str, data: Dict[str, Any]
    ) -> None:
        if page_id not in self._property_cache:
            self._property_cache[page_id] = {}
        self._property_cache[page_id][prop_name] = data

    def is_building_cache(self) -> bool:
        return self._is_building_cache

    def set_building_cache(self, value: bool) -> None:
        self._is_building_cache = value
