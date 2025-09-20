from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Union

from notionary.blocks.block_client import NotionBlockClient
from notionary.comments import CommentClient, Comment
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.database.database_client import NotionDatabaseClient
from notionary.file_upload.client import NotionFileUploadClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.schemas import NotionContentSchema
from notionary.page import page_context
from notionary.page.page_client import NotionPageClient
from notionary.page.page_content_deleting_service import PageContentDeletingService
from notionary.page.page_content_writer import PageContentWriter
from notionary.page.page_context import PageContextProvider, page_context
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.page.properties.page_property_reader import PagePropertyReader
from notionary.page.properties.page_property_writer import PagePropertyWriter
from notionary.page.properties.page_property_models import (
    PageProperty,
    PropertyType,
)
from notionary.util import LoggingMixin

from notionary.page.page_factory import (
    load_page_from_id,
    load_page_from_name,
    load_page_from_url,
)
from notionary.util.covers import get_random_gradient_cover

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionPage(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        title: str,
        url: str,
        archived: bool,
        in_trash: bool,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        properties: dict[str, PageProperty] | None = None,
        parent_database: NotionDatabase | None = None,
        token: str | None = None,
    ):
        self._page_id = page_id
        self._title = title
        self._url = url
        self._is_archived = archived
        self._is_in_trash = in_trash
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url
        self._properties = properties or {}
        self._parent_database = parent_database
        self.token = token

        self._page_client = NotionPageClient(
            page_id=page_id, properties=properties, token=token
        )
        self._block_client = NotionBlockClient(token=token)
        self._comment_client = CommentClient(token=token)

        self.block_element_registry = BlockRegistry()

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

        self.property_reader = PagePropertyReader(self)
        self.property_writer = PagePropertyWriter(self)

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: str | None = None
    ) -> NotionPage:
        return await load_page_from_id(page_id, token)

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: str | None = None, min_similarity: float = 0.6
    ) -> NotionPage:
        """
        Create a NotionPage by finding a page with fuzzy matching on the title.
        Uses Notion's search API and fuzzy matching to find the best result.
        """
        return await load_page_from_name(page_name, token, min_similarity)

    @classmethod
    async def from_url(cls, url: str, token: str | None= None) -> NotionPage:
        return await load_page_from_url(url, token)

    @property
    def id(self) -> str:
        return self._page_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def external_icon_url(self) -> str | None:
        return self._external_icon_url

    @property
    def emoji_icon(self) -> str | None:
        return self._emoji_icon

    @property
    def cover_image_url(self) -> str | None:
        return self._cover_image_url

    @property
    def properties(self) -> dict[str, PageProperty]:
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
        return await self._comment_client.list_all_comments_for_page(
            page_id=self._page_id
        )

    async def post_comment(
        self,
        rich_text_str: str,
        *,
        discussion_id: str | None = None,
    ) -> Comment:
        return await self._comment_client.create_comment(
            rich_text_str=rich_text_str,
            page_id=self._page_id,
            discussion_id=discussion_id,
        )

    async def set_title(self, title: str) -> None:
        await self.property_writer.set_title_property(title)

    async def append_markdown(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> None:
        async with page_context(self.page_context_provider):
            _ = await self._page_content_writer.append_markdown(content=content)

    async def replace_content(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> None:
        await self._page_content_deleting_service.clear_page_content()
        await self._page_content_writer.append_markdown(content=content)

    async def clear_page_content(self) -> None:
        await self._page_content_deleting_service.clear_page_content()

    async def get_markdown_content(self) -> str:
        blocks = await self._block_client.get_blocks_by_page_id_recursively(
            page_id=self._page_id
        )
        return await self._page_content_retriever.convert_to_markdown(blocks=blocks)

    async def set_emoji_icon(self, emoji: str) -> None:
        page_response = await self._page_client.patch_emoji_icon(emoji)

        self._emoji_icon = page_response.icon.emoji
        self._external_icon_url = None

    async def set_external_icon(self, url: str) -> None:
        page_response = await self._page_client.patch_external_icon(url)

        self._emoji_icon = None
        self._external_icon_url = page_response.icon.external.url

    async def remove_icon(self) -> None:
        await self._page_client.remove_icon()
        self._emoji_icon = None
        self._external_icon_url = None
        
    async def archive(self) -> None:
        if self._is_archived:
            self.logger.info("Page is already archived.")
            return

        page_response = await self._page_client.archive_page()
        self._is_archived = page_response.archived
        self.logger.info(f"Page {self._page_id} archived.")
        
    async def unarchive(self) -> None:
        if not self._is_archived:
            self.logger.info("Page is not archived.")
            return

        page_response = await self._page_client.unarchive_page()
        self._is_archived = page_response.archived
        self.logger.info(f"Page {self._page_id} unarchived.")

    async def create_child_database(self, title: str) -> NotionDatabase:
        from notionary import NotionDatabase

        database_client = NotionDatabaseClient(token=self._page_client.token)

        create_database_response = await database_client.create_database(
            title=title,
            parent_page_id=self._page_id,
        )

        return await NotionDatabase.from_database_id(
            id=create_database_response.id, token=self._page_client.token
        )

    async def set_cover(self, external_url: str) -> None:
        updated_page = await self._page_client.patch_external_cover(external_url)
        self._cover_image_url = updated_page.cover.external.url

    async def remove_cover(self) -> None:
        await self._page_client.remove_cover()
        self._cover_image_url = None

    async def set_random_gradient_cover(self) -> None:
        random_cover_url = get_random_gradient_cover()
        await self.set_cover(random_cover_url)

    async def get_property_value_by_name(self, property_name: str) -> Any:
        return await self.property_reader.get_property_value_by_name(property_name)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        if property_name not in self._properties:
            return []

        if not self._parent_database:
            return []

        return await self._parent_database.get_options_by_property_name(property_name)

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        return await self.property_writer.set_property_value_by_name(
            property_name, value
        )

    async def set_relation_property_by_relation_values(
        self, property_name: str, relation_values: list[str]
    ) -> None:
        if not self._parent_database:
            return

        property_type = self._parent_database.get_property_type(property_name)
        if property_type != PropertyType.RELATION:
            return

        await self.property_writer.set_relation_property_by_relation_values(
            property_name, relation_values
        )

    def _setup_page_context_provider(self) -> PageContextProvider:
        return PageContextProvider(
            page_id=self._page_id,
            database_client=NotionDatabaseClient(token=self._page_client.token),
            file_upload_client=NotionFileUploadClient(),
        )
