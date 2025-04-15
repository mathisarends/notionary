from typing import Dict, Any, List, Optional
from notionary.notion_client import NotionClient
from notionary.page.metadata.metadata_editor import MetadataEditor
from notionary.page.properites.property_operation_result import (
    PropertyOperationResult,
)
from notionary.page.relations.notion_page_title_resolver import (
    NotionPageTitleResolver,
)
from notionary.page.properites.database_property_service import (
    DatabasePropertyService,
)
from notionary.page.relations.page_database_relation import PageDatabaseRelation
from notionary.page.properites.property_value_extractor import (
    PropertyValueExtractor,
)
from notionary.util.logging_mixin import LoggingMixin


class PagePropertyManager(LoggingMixin):
    """Verwaltet den Zugriff auf und die Änderung von Seiteneigenschaften."""

    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        metadata_editor: MetadataEditor,
        db_relation: PageDatabaseRelation,
    ):
        self._page_id = page_id
        self._client = client
        self._page_data = None
        self._metadata_editor = metadata_editor
        self._db_relation = db_relation
        self._db_property_service = None

        self._extractor = PropertyValueExtractor(self.logger)
        self._title_resolver = NotionPageTitleResolver(client)

    async def get_properties(self) -> Dict[str, Any]:
        """Retrieves all properties of the page."""
        page_data = await self._get_page_data()
        if page_data and "properties" in page_data:
            return page_data["properties"]
        return {}

    async def get_property_value(self, property_name: str, relation_getter=None) -> Any:
        """
        Get the value of a specific property.

        Args:
            property_name: Name of the property to get
            relation_getter: Optional callback function to get relation values
        """
        properties = await self.get_properties()
        if property_name not in properties:
            return None

        prop_data = properties[property_name]
        return await self._extractor.extract(property_name, prop_data, relation_getter)

    async def set_property_by_name(
        self, property_name: str, value: Any
    ) -> PropertyOperationResult:
        """
        Set a property value by name, automatically detecting the property type.

        Args:
            property_name: Name of the property
            value: Value to set

        Returns:
            PropertyOperationResult: Result of the operation with status, error messages,
                                    and available options if applicable
        """
        property_type = await self.get_property_type(property_name)

        if property_type == "relation":
            result = PropertyOperationResult.from_relation_type_error(
                property_name, value
            )
            self.logger.warning(result.error)
            return result

        if not await self._db_relation.is_database_page():
            api_response = await self._metadata_editor.set_property_by_name(
                property_name, value
            )
            if api_response:
                await self.invalidate_cache()
                return PropertyOperationResult.from_success(
                    property_name, value, api_response
                )
            return PropertyOperationResult.from_no_api_response(property_name, value)

        db_service = await self._init_db_property_service()

        if not db_service:
            api_response = await self._metadata_editor.set_property_by_name(
                property_name, value
            )
            if api_response:
                await self.invalidate_cache()
                return PropertyOperationResult.from_success(
                    property_name, value, api_response
                )
            return PropertyOperationResult.from_no_api_response(property_name, value)

        is_valid, error_message, available_options = (
            await db_service.validate_property_value(property_name, value)
        )

        if not is_valid:
            if available_options:
                options_str = "', '".join(available_options)
                detailed_error = f"{error_message}\nAvailable options for '{property_name}': '{options_str}'"
                self.logger.warning(detailed_error)
            else:
                self.logger.warning(
                    "%s\nNo valid options available for '%s'",
                    error_message,
                    property_name,
                )

            return PropertyOperationResult.from_error(
                property_name, error_message, value, available_options
            )

        api_response = await self._metadata_editor.set_property_by_name(
            property_name, value
        )
        if api_response:
            await self.invalidate_cache()
            return PropertyOperationResult.from_success(
                property_name, value, api_response
            )

        return PropertyOperationResult.from_no_api_response(property_name, value)

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """Gets the type of a specific property."""
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """Gets the available option names for a property."""
        db_service = await self._init_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []

    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
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

        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service
