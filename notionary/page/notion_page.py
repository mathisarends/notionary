from __future__ import annotations
from typing import Any, Dict, List, Optional
import re

from notionary.elements.registry.block_element_registry import BlockElementRegistry
from notionary.elements.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.notion_client import NotionClient
from notionary.page.content.page_content_retriever import PageContentRetriever
from notionary.page.metadata.metadata_editor import MetadataEditor
from notionary.page.metadata.notion_icon_manager import NotionPageIconManager
from notionary.page.metadata.notion_page_cover_manager import (
    NotionPageCoverManager,
)
from notionary.page.properites.database_property_service import (
    DatabasePropertyService,
)
from notionary.page.relations.notion_page_relation_manager import (
    NotionPageRelationManager,
)
from notionary.page.content.page_content_writer import PageContentWriter
from notionary.page.properites.page_property_manager import PagePropertyManager
from notionary.page.relations.notion_page_title_resolver import NotionPageTitleResolver
from notionary.util.warn_direct_constructor_usage import warn_direct_constructor_usage
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import extract_and_validate_page_id
from notionary.page.relations.page_database_relation import PageDatabaseRelation


class NotionPage(LoggingMixin):
    """
    Managing content and metadata of a Notion page.
    """

    @warn_direct_constructor_usage
    def __init__(
        self,
        page_id: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self._page_id = extract_and_validate_page_id(page_id=page_id, url=url)
        self._url = url
        self._title = title
        self._client = NotionClient(token=token)
        self._page_data = None
        self._title_loaded = title is not None
        self._url_loaded = url is not None

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_full_registry()
        )

        self._page_content_writer = PageContentWriter(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )

        self._page_content_retriever = PageContentRetriever(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )

        self._metadata = MetadataEditor(self._page_id, self._client)
        self._page_cover_manager = NotionPageCoverManager(
            page_id=self._page_id, client=self._client
        )
        self._page_icon_manager = NotionPageIconManager(
            page_id=self._page_id, client=self._client
        )

        self._db_relation = PageDatabaseRelation(
            page_id=self._page_id, client=self._client
        )
        self._db_property_service = None

        self._relation_manager = NotionPageRelationManager(
            page_id=self._page_id, client=self._client
        )

        self._property_manager = PagePropertyManager(
            self._page_id, self._client, self._metadata, self._db_relation
        )

    @classmethod
    def from_page_id(cls, page_id: str, token: Optional[str] = None) -> NotionPage:
        """
        Create a NotionPage from a page ID.

        Args:
            page_id: The ID of the Notion page
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance
        """
        from notionary.page.notion_page_factory import NotionPageFactory

        cls.logger.info("Creating page from ID: %s", page_id)
        return NotionPageFactory().from_page_id(page_id, token)

    @classmethod
    def from_url(cls, url: str, token: Optional[str] = None) -> NotionPage:
        """
        Create a NotionPage from a Notion URL.

        Args:
            url: The URL of the Notion page
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance
        """
        from notionary.page.notion_page_factory import NotionPageFactory

        cls.logger.info("Creating page from URL: %s", url)
        return NotionPageFactory().from_url(url, token)

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage by finding a page with a matching name.
        Uses fuzzy matching to find the closest match to the given name.

        Args:
            page_name: The name of the Notion page to search for
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance
        """
        from notionary.page.notion_page_factory import NotionPageFactory

        return await NotionPageFactory().from_page_name(page_name, token)

    @property
    def id(self) -> str:
        """
        Get the ID of the page.
        """
        return self._page_id

    @property
    def block_registry(self) -> BlockElementRegistry:
        """
        Get the block element registry associated with this page.

        Returns:
            BlockElementRegistry: The registry of block elements.
        """
        return self._block_element_registry

    @block_registry.setter
    def block_registry(self, block_registry: BlockElementRegistry) -> None:
        """
        Set the block element registry for the page content manager.

        Args:
            block_registry: The registry of block elements to use.
        """
        self._block_element_registry = block_registry
        self._page_content_writer = PageContentRetriever(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )
        self._page_content_retriever = PageContentRetriever(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )

    def get_notion_markdown_syntax_prompt(self) -> str:
        """
        Get the formatting prompt for the page content manager.

        Returns:
            str: The formatting prompt.
        """
        return self._block_element_registry.generate_llm_prompt()

    async def get_title(self) -> str:
        """
        Get the title of the page, loading it if necessary.

        Returns:
            str: The page title.
        """
        if not self._title_loaded:
            self._title = await self._fetch_page_title()
        return self._title

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Set the title of the page.

        Args:
            title: The new title.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        result = await self._metadata.set_title(title)
        if result:
            self._title = title
            self._title_loaded = True
        return result

    async def get_url(self) -> str:
        """
        Get the URL of the page, constructing it if necessary.

        Returns:
            str: The page URL.
        """
        if not self._url_loaded:
            self._url = await self._generate_url_from_title()
            self._url_loaded = True
        return self._url

    async def append_markdown(self, markdown: str, append_divider=False) -> bool:
        """
        Append markdown content to the page.

        Args:
            markdown: The markdown content to append.

        Returns:
            str: Status or confirmation message.
        """
        return await self._page_content_writer.append_markdown(
            markdown_text=markdown, append_divider=append_divider
        )

    async def clear_page_content(self) -> bool:
        """
        Clear all content from the page.

        Returns:
            str: Status or confirmation message.
        """
        return await self._page_content_writer.clear_page_content()

    async def replace_content(self, markdown: str) -> bool:
        """
        Replace the entire page content with new markdown content.

        Args:
            markdown: The new markdown content.

        Returns:
            str: Status or confirmation message.
        """
        clear_result = await self._page_content_writer.clear_page_content()
        if not clear_result:
            self.logger.error("Failed to clear page content before replacement")
            return False

        return await self._page_content_writer.append_markdown(
            markdown_text=markdown, append_divider=False
        )

    async def get_text_content(self) -> str:
        """
        Get the text content of the page.

        Returns:
            str: The text content of the page.
        """
        return await self._page_content_retriever.get_page_content()

    async def get_icon(self) -> str:
        """
        Retrieve the page icon - either emoji or external URL.

        Returns:
            Optional[str]: The icon emoji or URL, or None if no icon is set.
        """
        return await self._page_icon_manager.get_icon()

    async def set_emoji_icon(self, emoji: str) -> Optional[str]:
        """
        Sets the page icon to an emoji.

        Args:
            emoji (str): The emoji character to set as the icon.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_icon_manager.set_emoji_icon(emoji=emoji)

    async def set_external_icon(self, url: str) -> Optional[str]:
        """
        Sets the page icon to an external image.

        Args:
            url (str): The URL of the external image to set as the icon.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_icon_manager.set_external_icon(external_icon_url=url)

    async def get_cover_url(self) -> Optional[str]:
        """
        Get the URL of the page cover image.

        Returns:
            str: The URL of the cover image or empty string if not available.
        """
        return await self._page_cover_manager.get_cover_url()

    async def set_cover(self, external_url: str) -> Optional[str]:
        """
        Set the cover image for the page using an external URL.

        Args:
            external_url: URL to the external image.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_cover_manager.set_cover(external_url)

    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """
        Set a random gradient as the page cover.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_cover_manager.set_random_gradient_cover()

    async def get_property_value_by_name(self, property_name: str) -> Any:
        """
        Get the value of a specific property.

        Args:
            property_name: The name of the property.

        Returns:
            Any: The value of the property.
        """
        properties = await self._property_manager._get_properties()

        if property_name not in properties:
            return None

        prop_data = properties[property_name]
        prop_type = prop_data.get("type")

        if prop_type == "relation":
            return await self._relation_manager.get_relation_values(property_name)

        return await self._property_manager.get_property_value(property_name)

    async def get_options_for_property(
        self, property_name: str, limit: int = 100
    ) -> List[str]:
        """
        Get the available options for a property (select, multi_select, status, relation).

        Args:
            property_name: The name of the property.
            limit: Maximum number of options to return (only affects relation properties).

        Returns:
            List[str]: List of available option names or page titles.
        """
        property_type = await self._get_property_type(property_name)

        if property_type is None:
            return []

        if property_type == "relation":
            return await self._relation_manager.get_relation_options(
                property_name, limit
            )

        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)

        return []

    async def set_property_value_by_name(
        self, property_name: str, value: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Set the value of a specific property by its name.

        Args:
            property_name: The name of the property.
            value: The new value to set.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._property_manager.set_property_by_name(
            property_name=property_name,
            value=value,
        )

    async def set_relation_property_values_by_name(
        self, relation_property_name: str, page_titles: List[str]
    ) -> List[str]:
        """
        Add one or more relations to a relation property.

        Args:
            relation_property_name: The name of the relation property.
            page_titles: A list of page titles to relate to.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._relation_manager.set_relation_values_by_page_titles(
            property_name=relation_property_name, page_titles=page_titles
        )

    async def get_relation_property_values_by_name(self, property_name: str) -> List[str]:
        """
        Return the current relation values for a property.

        Args:
            property_name: The name of the relation property.

        Returns:
            List[str]: List of relation values.
        """
        return await self._relation_manager.get_relation_values(property_name)

    async def get_last_edit_time(self) -> str:
        """
        Get the timestamp when the page was last edited.

        Returns:
            str: ISO 8601 formatted timestamp string of when the page was last edited.
        """
        try:
            page_response = await self._client.get_page(self._page_id)
            return (
                page_response.last_edited_time if page_response.last_edited_by else ""
            )

        except Exception as e:
            self.logger.error("Error retrieving last edited time: %s", str(e))
            return ""

    async def _fetch_page_title(self) -> str:
        """
        Load the page title from Notion API if not already loaded.

        Returns:
            str: The page title.
        """
        notion_page_title_resolver = NotionPageTitleResolver(self._client)
        return await notion_page_title_resolver.get_title_by_page_id(
            page_id=self._page_id
        )

    async def _generate_url_from_title(self) -> str:
        """
        Build a Notion URL from the page ID, including the title if available.

        Returns:
            str: The Notion URL for the page.
        """
        title = await self._fetch_page_title()

        url_title = ""
        if title and title != "Untitled":
            url_title = re.sub(r"[^\w\s-]", "", title)
            url_title = re.sub(r"[\s]+", "-", url_title)
            url_title = f"{url_title}-"

        clean_id = self._page_id.replace("-", "")

        return f"https://www.notion.so/{url_title}{clean_id}"

    async def _get_db_property_service(self) -> Optional[DatabasePropertyService]:
        """
        Gets the database property service, initializing it if necessary.
        This is a more intuitive way to work with the instance variable.

        Returns:
            Optional[DatabasePropertyService]: The database property service or None if not applicable
        """
        if self._db_property_service is not None:
            return self._db_property_service

        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None

        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service

    async def _get_property_type(self, property_name: str) -> Optional[str]:
        """
        Get the type of a specific property.

        Args:
            property_name: The name of the property.

        Returns:
            Optional[str]: The type of the property, or None if not found.
        """
        properties = await self._property_manager._get_properties()

        if property_name not in properties:
            return None

        prop_data = properties[property_name]
        return prop_data.get("type")
