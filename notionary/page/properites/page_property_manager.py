from typing import Callable, Dict, Any, List, Optional
from notionary.models.notion_page_response import NotionPageResponse
from notionary.page.metadata.metadata_editor import MetadataEditor
from notionary.page.properites.database_property_service import (
    DatabasePropertyService,
)
from notionary.page.relations.page_database_relation import PageDatabaseRelation
from notionary.util import LoggingMixin


class PagePropertyManager(LoggingMixin):
    """Verwaltet den Zugriff auf und die Änderung von Seiteneigenschaften."""

    def __init__(
        self,
        page_id: str,
        metadata_editor: MetadataEditor,
        db_relation: PageDatabaseRelation,
    ):
        self._page_id = page_id
        self._page_data = None
        self._metadata_editor = metadata_editor
        self._db_relation = db_relation
        self._db_property_service = None

    async def get_property_value(self, property_name: str, relation_getter=None) -> Any:
        """
        Get the value of a specific property.

        Args:
            property_name: Name of the property to get
            relation_getter: Optional callback function to get relation values
        """
        properties = await self._get_properties()
        if property_name not in properties:
            return None

        prop_data = properties[property_name]
        return self.extract_property_value(property_name, prop_data, relation_getter)

    async def set_property_by_name(
        self, property_name: str, value: Any
    ) -> Optional[Any]:
        """
        Set a property value by name, automatically detecting the property type.

        Args:
            property_name: Name of the property
            value: Value to set

        Returns:
            Optional[Any]: The new value if successful, None if failed
        """
        property_type = await self.get_property_type(property_name)

        if property_type == "relation":
            self.logger.warning(
                "Property '%s' is of type 'relation'. Relations must be set using the RelationManager.",
                property_name,
            )
            return None

        is_db_page = await self._db_relation.is_database_page()
        db_service = None

        if is_db_page:
            db_service = await self._init_db_property_service()

        if db_service:
            is_valid, error_message, available_options = (
                await db_service.validate_property_value(property_name, value)
            )

            if not is_valid:
                if available_options:
                    options_str = "', '".join(available_options)
                    self.logger.warning(
                        "%s\nAvailable options for '%s': '%s'",
                        error_message,
                        property_name,
                        options_str,
                    )
                else:
                    self.logger.warning(
                        "%s\nNo valid options available for '%s'",
                        error_message,
                        property_name,
                    )
                return None

        api_response = await self._metadata_editor.set_property_by_name(
            property_name, value
        )

        if api_response:
            await self.invalidate_cache()
            return value

        self.logger.warning(
            "Failed to set property '%s' (no API response)", property_name
        )
        return None

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """Gets the type of a specific property."""
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def _get_page_data(self, force_refresh=False) -> NotionPageResponse:
        """Gets the page data and caches it for future use."""
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data

    async def invalidate_cache(self) -> None:
        """Forces a refresh of the cached page data on next access."""
        self._page_data = None

    async def _init_db_property_service(self) -> Optional[DatabasePropertyService]:
        """Lazily initializes the database property service if needed."""
        if self._db_property_service is not None:
            return self._db_property_service

        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None

        self._db_property_service = DatabasePropertyService(database_id)
        await self._db_property_service.load_schema()
        return self._db_property_service

    async def _get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page."""
        page_data = await self._get_page_data()
        return page_data.properties if page_data.properties else {}

    def extract_property_value(
        self,
        prop_data: dict,
    ) -> Any:
        """
        Extract the value of a Notion property from its data dict.
        Supports all common Notion property types.
        """
        prop_type = prop_data.get("type")
        if not prop_type:
            return None

        handlers: dict[str, Callable[[], Any]] = {
            "title": lambda: "".join(
                t.get("plain_text", "") for t in prop_data.get("title", [])
            ),
            "rich_text": lambda: "".join(
                t.get("plain_text", "") for t in prop_data.get("rich_text", [])
            ),
            "number": lambda: prop_data.get("number"),
            "select": lambda: (
                prop_data.get("select", {}).get("name")
                if prop_data.get("select")
                else None
            ),
            "multi_select": lambda: [
                o.get("name") for o in prop_data.get("multi_select", [])
            ],
            "status": lambda: (
                prop_data.get("status", {}).get("name")
                if prop_data.get("status")
                else None
            ),
            "date": lambda: prop_data.get("date"),
            "checkbox": lambda: prop_data.get("checkbox"),
            "url": lambda: prop_data.get("url"),
            "email": lambda: prop_data.get("email"),
            "phone_number": lambda: prop_data.get("phone_number"),
            "people": lambda: [p.get("id") for p in prop_data.get("people", [])],
            "files": lambda: [
                (
                    f.get("external", {}).get("url")
                    if f.get("type") == "external"
                    else f.get("name")
                )
                for f in prop_data.get("files", [])
            ],
        }

        handler = handlers.get(prop_type)
        if handler is None:
            return None

        result = handler()
        return result
