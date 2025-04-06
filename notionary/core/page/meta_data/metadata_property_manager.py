from typing import Any, Dict, List, Optional
from notionary.core.notion_client import NotionClient
from notionary.core.page.meta_data.metadata_cache import MetadataCache
from notionary.core.page.property_formatter import NotionPropertyFormatter
from notionary.util.logging_mixin import LoggingMixin


class MetadataPropertManager(LoggingMixin):
    """Verwaltet Eigenschaften von Notion-Seiten."""

    def __init__(
        self,
        client: NotionClient,
        cache: MetadataCache,
        formatter: NotionPropertyFormatter,
    ):
        self._client = client
        self._cache = cache
        self._formatter = formatter

    async def find_property_by_type(self, page_id: str, prop_type: str) -> List[str]:
        """Findet alle Eigenschaften eines bestimmten Typs."""
        properties = self._cache.get_property_cache(page_id)
        if not properties:
            self.logger.warning("Keine Eigenschaften im Cache für Seite %s", page_id)
            return []

        return [
            name for name, info in properties.items() if info.get("type") == prop_type
        ]

    async def get_status_options(
        self, page_id: str, status_property_name: str
    ) -> List[Dict[str, Any]]:
        """Gibt die verfügbaren Optionen für eine Status-Eigenschaft zurück."""
        properties = self._cache.get_property_cache(page_id)

        if not properties:
            self.logger.warning("Keine Eigenschaften im Cache für Seite %s", page_id)
            return []

        if status_property_name not in properties:
            self.logger.error("Eigenschaft '%s' nicht gefunden", status_property_name)
            return []

        prop_info = properties[status_property_name]
        if prop_info["type"] != "status":
            self.logger.error(
                "Eigenschaft '%s' ist keine Status-Eigenschaft", status_property_name
            )
            return []

        if "options" in prop_info:
            return prop_info["options"]

        return []

    async def list_valid_status_options(
        self, page_id: str, status_property_name: str
    ) -> List[str]:
        """Gibt eine Liste aller gültigen Status-Optionen-Namen zurück."""
        options = await self.get_status_options(page_id, status_property_name)
        return [option["name"] for option in options]

    async def update_property(
        self, page_id: str, name: str, value: Any
    ) -> Optional[Dict[str, Any]]:
        """Aktualisiert eine einzelne Eigenschaft mit Typ-Validierung."""
        properties = self._cache.get_property_cache(page_id)

        if name not in properties:
            self.logger.error("Eigenschaft '%s' nicht gefunden", name)
            return None

        prop_info = properties[name]
        prop_type = prop_info["type"]

        if prop_type == "status":
            status_options = await self.get_status_options(page_id, name)
            status_names = [option["name"] for option in status_options]

            if status_names and str(value) not in status_names:
                self.logger.error(
                    "Ungültiger Status: '%s'. Verfügbare Optionen: %s",
                    value,
                    ", ".join(status_names),
                )
                return None

        formatted_prop = self._formatter.format_value(prop_type, value)
        if not formatted_prop:
            return None

        properties_data = {name: formatted_prop}

        result = await self._client.patch(
            f"pages/{page_id}", {"properties": properties_data}
        )

        if result:
            self._cache.clear_metadata(page_id)

        return result
