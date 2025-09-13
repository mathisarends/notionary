from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from notionary.blocks.client import NotionBlockClient
from notionary.comments import CommentClient, Comment
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.database.client import NotionDatabaseClient
from notionary.file_upload.client import NotionFileUploadClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.notion_client import NotionClient
from notionary.page.page_models import NotionPageUpdateDto
from notionary.schemas import NotionContentSchema
from notionary.page import page_context
from notionary.page.page_client import NotionPageClient
from notionary.page.page_content_deleting_service import PageContentDeletingService
from notionary.page.page_content_writer import PageContentWriter
from notionary.page.page_context import PageContextProvider, page_context
from notionary.page.property_formatter import NotionPropertyFormatter
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.page.utils import extract_property_value
from notionary.shared.models.property_models import PropertyType
from notionary.util import LoggingMixin

from notionary.page.page_factory import (
    load_page_from_id,
    load_page_from_name,
    load_page_from_url,
)


if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionPage(LoggingMixin):
    """
    Managing content and metadata of a Notion page.
    """

    def __init__(
        self,
        page_id: str,
        title: str,
        url: str,
        archived: bool,
        in_trash: bool,
        initial_page_schema: NotionPageUpdateDto,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        properties: dict[str, Any] | None = None,
        parent_database: NotionDatabase | None = None,
        token: str | None = None,
    ):
        """
        Initialize the page manager with all metadata.

        Note: Use factory methods (from_page_id, from_page_name, from_url)
        instead of direct instantiation.
        """
        self._page_id = page_id
        self._title = title
        self._url = url
        self._is_archived = archived
        self._is_in_trash = in_trash
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url
        self._properties = properties
        self._parent_database = parent_database
        self.token = token

        self._page_client = NotionPageClient(
            page_id=page_id, initial_page_schema=initial_page_schema, token=token
        )
        self._block_client = NotionBlockClient(token=token)
        self._comment_client = CommentClient(token=token)
        self._page_data = None

        self.block_element_registry = BlockRegistry.create_registry()

        self._page_content_writer = PageContentWriter(
            page_id=self._page_id,
            block_registry=self.block_element_registry,
        )

        self._page_content_deleting_service = PageContentDeletingService(
            page_id=self._page_id,
            block_registry=self.block_element_registry,
        )

        self._page_content_retriever = PageContentRetriever(
            block_registry=self.block_element_registry,
        )

        self.page_context_provider = self._setup_page_context_provider()

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage from a page ID.
        """
        # Lazy import to avoid potential circular dependencies
        return await load_page_from_id(page_id, token)

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: Optional[str] = None, min_similarity: float = 0.6
    ) -> NotionPage:
        """
        Create a NotionPage by finding a page with fuzzy matching on the title.
        Uses Notion's search API and fuzzy matching to find the best result.
        """
        return await load_page_from_name(page_name, token, min_similarity)

    @classmethod
    async def from_url(cls, url: str, token: Optional[str] = None) -> NotionPage:
        """
        Create a NotionPage from a Notion page URL.
        """
        return await load_page_from_url(url, token)

    @property
    def id(self) -> str:
        """Get the ID of the page."""
        return self._page_id

    @property
    def title(self) -> str:
        """Get the title of the page."""
        return self._title

    @property
    def url(self) -> str:
        """Get the URL of the page."""
        return self._url

    @property
    def external_icon_url(self) -> Optional[str]:
        """Get the external icon URL of the page."""
        return self._external_icon_url

    @property
    def emoji_icon(self) -> Optional[str]:
        """Get the emoji icon of the page."""
        return self._emoji_icon

    @property
    def cover_image_url(self) -> Optional[str]:
        """Get the cover image URL of the page."""
        return self._cover_image_url

    @property
    def properties(self) -> Optional[dict[str, Any]]:
        """Get the properties of the page."""
        return self._properties

    @property
    def is_archived(self) -> bool:
        return self._is_archived

    @property
    def is_in_trash(self) -> bool:
        return self._is_in_trash

    def get_prompt_information(self) -> str:
        markdown_syntax_builder = SyntaxPromptBuilder()
        return markdown_syntax_builder.build_concise_reference()

    async def get_comments(self) -> list[Comment]:
        """
        Get all comments for this page.
        """
        return await self._comment_client.list_all_comments_for_page(
            page_id=self._page_id
        )

    async def post_comment(
        self,
        rich_text_str: str,
        *,
        discussion_id: Optional[str] = None,
    ) -> Comment:
        """
        Post a comment on this page.
        """
        return await self._comment_client.create_comment(
            rich_text_str=rich_text_str,
            page_id=self._page_id,
            discussion_id=discussion_id,
        )

    async def set_title(self, title: str) -> str:
        """
        Set the title of the page.
        """
        await self._page_client.patch_title(title)
        self._title = title
        return title

    async def append_markdown(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> bool:
        """
        Append markdown content to the page.
        """
        async with page_context(self.page_context_provider):
            result = await self._page_content_writer.append_markdown(content=content)
            return result is not None

    async def replace_content(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> bool:
        """
        Replace the entire page content with new markdown content.

        Args:
            content: Either raw markdown text, a callback function that receives a MarkdownBuilder,
                    a MarkdownDocumentModel, or a NotionContentSchema
        """
        # Clear existing content first
        await self._page_content_deleting_service.clear_page_content()

        # Add new content
        result = await self._page_content_writer.append_markdown(content=content)
        return result is not None

    async def clear_page_content(self) -> str:
        """
        Clear all content from the page.
        """
        return await self._page_content_deleting_service.clear_page_content()

    async def get_text_content(self) -> str:
        """
        Get the text content of the page.
        """
        blocks = await self._block_client.get_blocks_by_page_id_recursively(
            page_id=self._page_id
        )
        return await self._page_content_retriever.convert_to_markdown(blocks=blocks)

    async def set_emoji_icon(self, emoji: str) -> str:
        """
        Sets the page icon to an emoji.
        """
        page_response = await self._page_client.patch_emoji_icon(emoji)

        self._emoji_icon = page_response.icon.emoji
        self._external_icon_url = None
        return page_response.icon.emoji

    async def set_external_icon(self, url: str) -> str:
        """
        Sets the page icon to an external image.
        """
        page_response = await self._page_client.patch_external_icon(url)

        self._emoji_icon = None
        self._external_icon_url = page_response.icon.external.url
        return page_response.icon.external.url

    async def remove_icon(self) -> None:
        """
        Removes the icon from the page.
        """
        _ = await self._page_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None

    async def create_child_database(self, title: str) -> NotionDatabase:
        """
        Create a child database within this page.
        """
        from notionary import NotionDatabase

        database_client = NotionDatabaseClient(token=self._page_client.token)

        create_database_response = await database_client.create_database(
            title=title,
            parent_page_id=self._page_id,
        )

        return await NotionDatabase.from_database_id(
            id=create_database_response.id, token=self._page_client.token
        )

    async def set_cover(self, external_url: str) -> str:
        """
        Set the cover image for the page using an external URL.
        """
        updated_page = await self._page_client.patch_external_cover(external_url)
        self._cover_image_url = updated_page.cover.external.url
        return updated_page.cover.external.url

    async def remove_cover(self) -> None:
        """
        Removes the cover image from the page.
        """
        _ = await self._page_client.remove_cover()
        self._cover_image_url = None

    async def set_random_gradient_cover(self) -> str:
        """
        Set a random gradient as the page cover.
        """
        random_cover_url = self._get_random_gradient_cover()
        return await self.set_cover(random_cover_url)

    async def archive(self) -> None:
        """
        Archive the page by moving it to the trash.
        """
        _ = await self._page_client.archive_page()

    async def unarchive(self) -> None:
        """
        Unarchive the page by restoring it from the trash.
        """
        _ = await self._page_client.unarchive_page()

    async def get_property_value_by_name(self, property_name: str) -> Any:
        """
        Get the value of a specific property.

        Returns None if property doesn't exist.
        """
        if property_name not in self._properties:
            return None

        property_schema: dict = self._properties.get(property_name)
        property_type = property_schema.get("type")

        if property_type == PropertyType.RELATION:
            return await self._get_relation_property_values_by_name(property_name)

        return extract_property_value(property_schema)

    async def _get_relation_property_values_by_name(
        self, property_name: str
    ) -> list[str]:
        """
        Retrieve the titles of all related pages for a relation property.
        """
        page_property_schema = self._properties.get(property_name)
        relation_page_ids = [
            rel.get("id") for rel in page_property_schema.get("relation", [])
        ]

        # Use factory function instead of direct instantiation
        notion_pages = [
            await load_page_from_id(page_id) for page_id in relation_page_ids
        ]
        return [page.title for page in notion_pages if page]

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        """
        Get the available options for a property (select, multi_select, status, relation).
        Returns empty list if property doesn't exist or has no options.
        """
        if property_name not in self.properties:
            return []

        property_schema: dict = self.properties.get(property_name)
        property_type = property_schema.get("type")

        if property_type in [PropertyType.SELECT, PropertyType.MULTI_SELECT, PropertyType.STATUS]:
            options = property_schema.get(property_type, {}).get("options", [])
            return [option.get("name", "") for option in options]

        if property_type == PropertyType.RELATION and self._parent_database:
            return await self._parent_database._get_relation_options(property_name)

        return []

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        """
        Set the value of a specific property by its name.
        Returns None if page has no parent database or property doesn't exist.
        """
        if not self._parent_database:
            return None

        property_type = self._parent_database.properties.get(property_name).get("type")

        if not property_type:
            return None

        if property_type == PropertyType.RELATION:
            return await self.set_relation_property_values_by_name(
                property_name=property_name, page_titles=value
            )

        property_formatter = NotionPropertyFormatter()
        update_data = property_formatter.format_value(
            property_name=property_name, property_type=property_type, value=value
        )

        updated_page_response = await self._page_client.patch_page(
            page_id=self._page_id, data=update_data
        )
        self._properties = updated_page_response.properties
        return extract_property_value(self._properties.get(property_name))

    async def set_relation_property_values_by_name(
        self, property_name: str, page_titles: list[str]
    ) -> list[str]:
        """
        Add one or more relations to a relation property.
        Returns empty list if page has no parent database or property is not a relation.
        """
        if not self._parent_database:
            return []

        property_type = self._parent_database.properties.get(property_name).get("type")

        if property_type != PropertyType.RELATION:
            return []

        relation_pages = await asyncio.gather(
            *(
                self._load_page_from_name_helper(page_title)
                for page_title in page_titles
            )
        )

        relation_page_ids = [page.id for page in relation_pages]

        property_formatter = NotionPropertyFormatter()

        update_data = property_formatter.format_value(
            property_name=property_name,
            property_type=PropertyType.RELATION,
            value=relation_page_ids,
        )

        updated_page_response = await self._page_client.patch_page(
            page_id=self._page_id, data=update_data
        )
        self._properties = updated_page_response.properties
        return page_titles

    async def _load_page_from_name_helper(self, page_title: str) -> NotionPage:
        """Helper method to avoid direct factory import in gather."""
        return await load_page_from_name(page_name=page_title)

    def _setup_page_context_provider(self) -> PageContextProvider:
        return PageContextProvider(
            page_id=self._page_id,
            database_client=NotionDatabaseClient(token=self._page_client.token),
            file_upload_client=NotionFileUploadClient(),
        )

    def _get_random_gradient_cover(self) -> str:
        import random

        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 10)
        ]
        return random.choice(default_notion_covers)
