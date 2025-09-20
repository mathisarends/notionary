from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from notionary.blocks.client import NotionBlockClient
from notionary.comments import CommentClient, Comment
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.database.database_client import NotionDatabaseClient
from notionary.file_upload.client import NotionFileUploadClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.page.page_models import NotionPageUpdateDto
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
    PageRelationProperty,
    PagePropertyT,
)
from notionary.util import LoggingMixin

from notionary.page.page_factory import (
    load_page_from_id,
    load_page_from_name,
    load_page_from_url,
)

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
        initial_page_schema: NotionPageUpdateDto,
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
            page_id=page_id, initial_page_schema=initial_page_schema, token=token
        )
        self._block_client = NotionBlockClient(token=token)
        self._comment_client = CommentClient(token=token)
        self._page_data = None

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

        # Initialize property reader and writer for consistent property handling
        self._property_reader = PagePropertyReader(self)
        self._property_writer = PagePropertyWriter(self)

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
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
        discussion_id: Optional[str] = None,
    ) -> Comment:
        return await self._comment_client.create_comment(
            rich_text_str=rich_text_str,
            page_id=self._page_id,
            discussion_id=discussion_id,
        )

    async def set_title(self, title: str) -> None:
        await self._property_writer.set_title_property(title)

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
        _ = await self._page_content_writer.append_markdown(content=content)

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
        random_cover_url = self._get_random_gradient_cover()
        await self.set_cover(random_cover_url)

    async def archive(self) -> None:
        await self._page_client.archive_page()

    async def unarchive(self) -> None:
        await self._page_client.unarchive_page()

    async def get_property_value_by_name(self, property_name: str) -> Any:
        return await self._property_reader.get_property_value_by_name(property_name)

    # Maybe even remove these and only allow over property reader itself (api is too much here)
    def get_value_of_status_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_status_property(name)

    def get_value_of_select_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_select_property(name)

    async def get_value_of_title_property(self, name: str) -> str:
        return await self._property_reader.get_value_of_title_property(name)

    async def get_values_of_people_property(self, property_name: str) -> list[str]:
        return self._property_reader.get_values_of_people_property(property_name)

    def get_value_of_created_time_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_created_time_property(name)

    async def get_values_of_relation_property(self, name: str) -> list[str]:
        return await self._property_reader.get_values_of_relation_property(name)

    def get_values_of_multiselect_property(self, name: str) -> list[str]:
        return self._property_reader.get_values_of_multiselect_property(name)

    def get_value_of_url_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_url_property(name)

    def get_value_of_number_property(self, name: str) -> float | None:
        return self._property_reader.get_value_of_number_property(name)

    def get_value_of_checkbox_property(self, name: str) -> bool:
        return self._property_reader.get_value_of_checkbox_property(name)

    def get_value_of_date_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_date_property(name)

    async def get_value_of_rich_text_property(self, name: str) -> str:
        return await self._property_reader.get_value_of_rich_text_property(name)

    def get_value_of_email_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_email_property(name)

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        return self._property_reader.get_value_of_phone_number_property(name)

    async def get_rich_text_plain(self, property_name: str) -> str:
        return await self._property_reader.get_value_of_rich_text_property(property_name)

    async def set_rich_text_property_by_name(
        self, property_name: str, text: str
    ) -> None:
        await self._property_writer.set_rich_text_property(property_name, text)

    async def set_url_property_by_name(self, property_name: str, url: str) -> None:
        await self._property_writer.set_url_property(property_name, url)

    async def set_email_property_by_name(self, property_name: str, email: str) -> None:
        await self._property_writer.set_email_property(property_name, email)

    async def set_phone_number_property_by_name(
        self, property_name: str, phone: str
    ) -> None:
        await self._property_writer.set_phone_number_property(property_name, phone)

    async def set_number_property_by_name(
        self, property_name: str, number: Union[int, float]
    ) -> None:
        await self._property_writer.set_number_property(property_name, number)

    async def set_checkbox_property_by_name(
        self, property_name: str, checked: bool
    ) -> None:
        await self._property_writer.set_checkbox_property(property_name, checked)

    async def set_select_property_by_name(
        self, property_name: str, option_name: str
    ) -> None:
        await self._property_writer.set_select_property(property_name, option_name)

    async def set_multi_select_property_by_name(
        self, property_name: str, option_names: list[str]
    ) -> None:
        await self._property_writer.set_multi_select_property(property_name, option_names)

    async def set_date_property_by_name(
        self, property_name: str, date_value: Union[str, dict]
    ) -> None:
        await self._property_writer.set_date_property(property_name, date_value)

    async def set_status_property_by_name(
        self, property_name: str, status_name: str
    ) -> None:
        await self._property_writer.set_status_property(property_name, status_name)

    async def set_relation_property_by_name(
        self, property_name: str, relation_ids: Union[str, list[str]]
    ) -> None:
        await self._property_writer.set_relation_property(property_name, relation_ids)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        if property_name not in self._properties:
            return []

        if not self._parent_database:
            return []

        return await self._parent_database.get_options_by_property_name(property_name)

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        return await self._property_writer.set_property_value_by_name(property_name, value)

    async def set_relation_property_values_by_name(
        self, property_name: str, page_titles: list[str]
    ) -> None:
        if not self._parent_database:
            return

        property_type = self._parent_database.get_property_type(property_name)
        if property_type != PropertyType.RELATION:
            return

        page_ids = await self._convert_page_titles_to_ids(page_titles)
        await self.set_relation_property_by_name(property_name, page_ids)

    async def _convert_page_titles_to_ids(self, page_titles: list[str]) -> list[str]:
        if not page_titles:
            return []

        pages = await asyncio.gather(
            *[
                load_page_from_name(
                    page_name=title,
                    token=self.token,
                )
                for title in page_titles
            ]
        )

        page_ids = [page.id for page in pages]
        return page_ids

    async def _get_relation_property_values_from_typed(
        self, relation_prop: PageRelationProperty
    ) -> list[str]:
        relation_page_ids = [rel.id for rel in relation_prop.relation]

        notion_pages = [
            await load_page_from_id(page_id) for page_id in relation_page_ids
        ]
        return [page.title for page in notion_pages if page]

    def _extract_property_value_fallback(self, property_dict: dict) -> Any:
        property_type = property_dict.get("type")
        return property_dict.get(property_type)

    def _setup_page_context_provider(self) -> PageContextProvider:
        return PageContextProvider(
            page_id=self._page_id,
            database_client=NotionDatabaseClient(token=self._page_client.token),
            file_upload_client=NotionFileUploadClient(),
        )

    def _get_random_gradient_cover(self) -> str:
        from random import choice

        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 10)
        ]
        return choice(default_notion_covers)

    def _get_property(
        self, name: str, property_type: type[PagePropertyT]
    ) -> PagePropertyT | None:
        """Get a property by name and type with type safety."""
        prop = self._properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None

