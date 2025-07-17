from __future__ import annotations
import random
from typing import Any, Dict, List, Optional
import re

from notionary.elements.registry.block_registry import BlockRegistry
from notionary.elements.registry.block_registry_builder import BlockRegistryBuilder
from notionary.models.notion_database_response import NotionPageResponse
from notionary.page.notion_page_client import NotionPageClient
from notionary.page.content.page_content_retriever import PageContentRetriever
from notionary.page.metadata.metadata_editor import MetadataEditor
from notionary.page.properites.database_property_service import (
    DatabasePropertyService,
)
from notionary.page.relations.notion_page_relation_manager import (
    NotionPageRelationManager,
)
from notionary.page.content.page_content_writer import PageContentWriter
from notionary.page.properites.page_property_manager import PagePropertyManager
from notionary.page.relations.notion_page_title_resolver import NotionPageTitleResolver
from notionary.util.factory_decorator import factory_only
from notionary.util import LoggingMixin
from notionary.util import format_uuid
from notionary.page.relations.page_database_relation import PageDatabaseRelation


class NotionPage(LoggingMixin):
    """
    Managing content and metadata of a Notion page.
    """

    @factory_only("from_page_id", "from_url", "from_page_name")
    def __init__(
        self,
        page_id: str,
        title: str,
        url: str,
        emoji: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """
        Initialize the page manager with all metadata.
        """
        self._page_id = page_id
        self._title = title
        self._url = url
        self._emoji_icon = emoji

        self._client = NotionPageClient(token=token)
        self._page_data = None

        self._block_element_registry = BlockRegistryBuilder.create_full_registry()

        self._page_content_writer = PageContentWriter(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )

        self._page_content_retriever = PageContentRetriever(
            page_id=self._page_id,
            block_registry=self._block_element_registry,
        )

        self._metadata = MetadataEditor(self._page_id, self._client)

        self._db_relation = PageDatabaseRelation(
            page_id=self._page_id, client=self._client
        )
        self._db_property_service = None

        self._relation_manager = NotionPageRelationManager(
            page_id=self._page_id, client=self._client
        )

        self._property_manager = PagePropertyManager(
            self._page_id, self._metadata, self._db_relation
        )

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage from a page ID.

        Args:
            page_id: The ID of the Notion page
            token: Optional Notion API token (uses environment variable if not provided)
        """
        formatted_id = format_uuid(page_id) or page_id

        async with NotionPageClient(token=token) as client:
            page_response = await client.get_page(formatted_id)
            return cls._create_from_response(page_response, formatted_id, token)

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage by finding a page with a matching name.
        Uses Notion's search API and takes the first (best) result.
        """
        from notionary.workspace.workspace import NotionWorkspace

        cls.logger.debug("Searching for page with name: %s", page_name)
        workspace = NotionWorkspace()

        try:
            cls.logger.debug("Using search endpoint to find pages")

            search_results = await workspace.search_pages(page_name)

            if not search_results:
                cls.logger.warning("No pages found for name: %s", page_name)
                raise ValueError(f"No pages found for name: {page_name}")

            # Get the first result and fetch its full data
            first_result = search_results[0]
            page_id = first_result.id

            async with NotionPageClient(token=token) as client:
                page_response = await client.get_page(page_id)
                instance = cls._create_from_response(page_response, page_id, token)

                cls.logger.info(
                    "Found matching page: '%s' (ID: %s)", instance.title, page_id
                )
                return instance

        except Exception as e:
            cls.logger.error("Error finding page by name: %s", str(e))
            raise

    @property
    def id(self) -> str:
        """
        Get the ID of the page.
        """
        return self._page_id

    @property
    def title(self) -> str:
        """
        Get the title of the page.
        """
        return self._title

    @property
    def url(self) -> str:
        """
        Get the URL of the page.
        If not set, generate it from the title and ID.
        """
        return self._url

    @property
    def emoji_icon(self) -> Optional[str]:
        """
        Get the emoji icon of the page.
        """
        return self._emoji_icon

    @property
    def block_registry(self) -> BlockRegistry:
        """
        Get the block element registry associated with this page.

        Returns:
            BlockElementRegistry: The registry of block elements.
        """
        return self._block_element_registry

    @property
    def block_registry_builder(self) -> BlockRegistryBuilder:
        """
        Get the block element registry builder associated with this page.

        Returns:
            BlockElementRegistryBuilder: The builder for block elements.
        """
        return self._block_element_registry.builder

    @block_registry.setter
    def block_registry(self, block_registry: BlockRegistry) -> None:
        """
        Set the block element registry for the page content manager.

        Args:
            block_registry: The registry of block elements to use.
        """
        self._block_element_registry = block_registry
        self._page_content_writer = PageContentWriter(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )
        self._page_content_retriever = PageContentRetriever(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )

    def get_notion_markdown_system_prompt(self) -> str:
        """
        Get the formatting prompt for the page content manager.

        Returns:
            str: The formatting prompt.
        """
        return self._block_element_registry.get_notion_markdown_syntax_prompt()

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Set the title of the page.
        """
        try:
            data = {
                "properties": {
                    "title": {"title": [{"type": "text", "text": {"content": title}}]}
                }
            }

            await self._client.patch_page(self._page_id, data)

            self._title = title
            return title

        except Exception as e:
            self.logger.error("Error setting page title: %s", str(e))
            return None

    async def get_url(self) -> str:
        """
        Get the URL of the page, constructing it if necessary.

        Returns:
            str: The page URL.
        """
        self.url
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

    async def set_emoji_icon(self, emoji: str) -> Optional[str]:
        """
        Sets the page icon to an emoji.
        """
        try:
            icon = {"type": "emoji", "emoji": emoji}
            page_response = await self._client.patch_page(
                page_id=self._page_id, data={"icon": icon}
            )

            self._emoji = page_response.icon.emoji
            return page_response.icon.emoji
        except Exception as e:

            self.logger.error(f"Error updating page emoji: {str(e)}")
            return None

    async def set_external_icon(self, url: str) -> Optional[str]:
        """
        Sets the page icon to an external image.
        """
        try:
            icon = {"type": "external", "external": {"url": url}}
            page_response = await self._client.patch_page(
                page_id=self._page_id, data={"icon": icon}
            )

            # For external icons, we clear the emoji since we now have external icon
            self._emoji = None
            self.logger.info(f"Successfully updated page external icon to: {url}")
            return page_response.icon.external.url

        except Exception as e:
            self.logger.error(f"Error updating page external icon: {str(e)}")
            return None

    async def get_cover_url(self) -> Optional[str]:
        """
        Get the URL of the page cover image.
        """
        try:
            page_data = await self._client.get_page(self.id)
            if not page_data or not page_data.cover:
                return None
            if page_data.cover.type == "external":
                return page_data.cover.external.url
        except Exception as e:
            self.logger.error(f"Error fetching cover URL: {str(e)}")
            return None

    async def set_cover(self, external_url: str) -> Optional[str]:
        """
        Set the cover image for the page using an external URL.
        """
        data = {"cover": {"type": "external", "external": {"url": external_url}}}
        try:
            updated_page = await self._client.patch_page(self.id, data=data)
            return updated_page.cover.external.url
        except Exception as e:
            self.logger.error("Failed to set cover image: %s", str(e))
            return None

    async def set_random_gradient_cover(self) -> Optional[str]:
        """
        Set a random gradient as the page cover.
        """
        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 12)
        ]
        random_cover_url = random.choice(default_notion_covers)
        return await self.set_cover(random_cover_url)

    async def get_property_value_by_name(self, property_name: str) -> Any:
        """
        Get the value of a specific property.
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

    async def get_relation_property_values_by_name(
        self, property_name: str
    ) -> List[str]:
        """
        Return the current relation values for a property.

        Args:
            property_name: The name of the relation property.

        Returns:
            List[str]: List of relation values.
        """
        return await self._relation_manager.get_relation_values(property_name)

    async def archive(self) -> bool:
        """
        Archive the page by moving it to the trash.
        """
        try:
            result = await self._client.patch_page(
                page_id=self._page_id, data={"archived": True}
            )
            return result is not None
        except Exception as e:
            self.logger.error("Error archiving page %s: %s", self._page_id, str(e))
            return False

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

        self._db_property_service = DatabasePropertyService(database_id)
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

    @classmethod
    def _create_from_response(
        cls,
        page_response: NotionPageResponse,
        page_id: str,
        token: Optional[str],
    ) -> NotionPage:
        """
        Create NotionPage instance from API response.
        """
        title = cls._extract_title(page_response)
        emoji = cls._extract_emoji(page_response)

        instance = cls(
            page_id=page_id,
            title=title,
            url=page_response.url,
            emoji=emoji,
            token=token,
        )

        cls.logger.info("Created page manager: '%s' (ID: %s)", title, page_id)
        return instance

    @staticmethod
    def _extract_title(page_response: NotionPageResponse) -> str:
        """Extract title from database response. Returns empty string if not found."""
        try:
            return page_response.properties["title"]["title"][0]["plain_text"]
        except (KeyError, IndexError, TypeError):
            return ""

    @staticmethod
    def _extract_emoji(page_response: NotionPageResponse) -> Optional[str]:
        """Extract emoji from database response."""
        if not page_response.icon:
            return None

        if page_response.icon.type == "emoji":
            return page_response.icon.emoji

        return None
