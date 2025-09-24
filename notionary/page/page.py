from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from notionary.blocks.block_http_client import NotionBlockHttpClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.comments import Comment, CommentClient
from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.file_upload.file_upload_http_client import FileUploadHttpClient
from notionary.page.page_content_deleting_service import PageContentDeletingService
from notionary.page.page_content_writer import PageContentWriter
from notionary.page.page_context import PageContextProvider, page_context
from notionary.page.page_factory import (
    load_page_from_id,
    load_page_from_title,
)
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.page_property_models import (
    PageProperty,
    PropertyType,
)
from notionary.page.properties.page_property_reader import PagePropertyReader
from notionary.page.properties.page_property_writer import PagePropertyWriter
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.schemas import NotionContentSchema
from notionary.shared.entities.entity import NotionEntity

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionPage(NotionEntity):
    def __init__(
        self,
        id: str,
        title: str,
        url: str,
        archived: bool,
        in_trash: bool,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        properties: dict[str, PageProperty] | None = None,
        parent_database: NotionDatabase | None = None,
    ):
        super().__init__(
            id=id,
            title=title,
            url=url,
            archived=archived,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._page_id = id
        self._properties = properties or {}
        self._parent_database = parent_database

        self._page_client = NotionPageHttpClient(page_id=id, properties=properties)
        self._block_client = NotionBlockHttpClient()
        self._comment_client = CommentClient()

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

        self._metadata_update_client = PageMetadataUpdateClient(page_id=id)

    @classmethod
    async def from_id(cls, id: str) -> NotionPage:
        return await load_page_from_id(id)

    @classmethod
    async def from_title(cls, title: str, min_similarity: float = 0.6) -> NotionPage:
        return await load_page_from_title(title, min_similarity)

    @property
    def _entity_metadata_update_client(self) -> PageMetadataUpdateClient:
        """Return the concrete metadata client for this entity."""
        return self._metadata_update_client

    @property
    def id(self) -> str:
        return self._page_id

    @property
    def properties(self) -> dict[str, PageProperty]:
        return self._properties

    def get_prompt_information(self) -> str:
        markdown_syntax_builder = SyntaxPromptBuilder()
        return markdown_syntax_builder.build_concise_reference()

    async def get_comments(self) -> list[Comment]:
        return await self._comment_client.list_all_comments_for_page(page_id=self._page_id)

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
        self._title = title

    async def append_markdown(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> None:
        async with page_context(self.page_context_provider):
            _ = await self._page_content_writer.append_markdown(content=content)

    async def replace_content(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> None:
        await self._page_content_deleting_service.clear_page_content()
        await self._page_content_writer.append_markdown(content=content)

    async def clear_page_content(self) -> None:
        await self._page_content_deleting_service.clear_page_content()

    async def get_markdown_content(self) -> str:
        blocks = await self._block_client.get_blocks_by_page_id_recursively(page_id=self._page_id)
        return await self._page_content_retriever.convert_to_markdown(blocks=blocks)

    async def create_child_database(self, title: str) -> NotionDatabase:
        from notionary import NotionDatabase

        # Use a temporary database_id since this creates a new database
        async with NotionDatabseHttpClient(database_id=self._parent_database.id or "temp") as database_client:
            create_database_response = await database_client.create_database(
                title=title,
                parent_page_id=self._page_id,
            )

        return await NotionDatabase.from_id(create_database_response.id)

    async def get_property_value_by_name(self, property_name: str) -> Any:
        return await self.property_reader.get_property_value_by_name(property_name)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        if property_name not in self._properties:
            return []

        if not self._parent_database:
            return []

        return await self._parent_database.get_options_by_property_name(property_name)

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        return await self.property_writer.set_property_value_by_name(property_name, value)

    async def set_relation_property_by_relation_values(self, property_name: str, relation_values: list[str]) -> None:
        if not self._parent_database:
            return

        property_type = self._parent_database.get_property_type(property_name)
        if property_type != PropertyType.RELATION:
            return

        await self.property_writer.set_relation_property_by_relation_values(property_name, relation_values)

    def _setup_page_context_provider(self) -> PageContextProvider:
        parent_database_id = self._parent_database.id if self._parent_database else "temp"

        return PageContextProvider(
            page_id=self._page_id,
            database_client=NotionDatabseHttpClient(parent_database_id),
            file_upload_client=FileUploadHttpClient(),
        )
