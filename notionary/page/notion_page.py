from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from notionary.blocks.block_http_client import NotionBlockHttpClient
from notionary.comments import CommentClient, Comment
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.file_upload.client import FileUploadHttpClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.page.page_models import NotionPageUpdateDto
from notionary.schemas import NotionContentSchema
from notionary.page import page_context
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_content_deleting_service import PageContentDeletingService
from notionary.page.page_content_writer import PageContentWriter
from notionary.page.page_context import PageContextProvider, page_context
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.page.properties.page_property_models import (
    PageProperty,
    PropertyType,
    PageStatusProperty,
    PageRelationProperty,
    PageMultiSelectProperty,
    PageSelectProperty,  # Added
    PageURLProperty,
    PageNumberProperty,
    PageCheckboxProperty,
    PageDateProperty,
    PageTitleProperty,  # Added
    PageRichTextProperty,
    PageEmailProperty,
    PagePhoneNumberProperty,
    PagePeopleProperty,  # Added
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
        properties: dict[str, PageProperty] | None = None,
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
        self._properties = properties or {}
        self._parent_database = parent_database
        self.token = token

        self._page_client = NotionPageHttpClient(
            page_id=page_id, initial_page_schema=initial_page_schema, token=token
        )
        self._block_client = NotionBlockHttpClient(token=token)
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

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage from a page ID.
        """
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
    def properties(self) -> dict[str, PageProperty]:
        """Get the typed properties of the page."""
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
    ) -> None:
        """
        Append markdown content to the page.
        """
        async with page_context(self.page_context_provider):
            _ = await self._page_content_writer.append_markdown(content=content)

    async def replace_content(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> None:
        """
        Replace the entire page content with new markdown content.
        """
        await self._page_content_deleting_service.clear_page_content()
        _ = await self._page_content_writer.append_markdown(content=content)

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

        database_client = NotionDatabseHttpClient(token=self._page_client.token)

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
        """Get the value of a specific property using typed properties."""
        prop = self._properties.get(property_name)
        if not prop:
            return

        # check for unknown types first
        if isinstance(prop, dict):
            return self._extract_property_value_fallback(prop)

        prop_type = prop.type

        if prop_type == PropertyType.STATUS:
            return self.get_value_of_status_property(property_name)

        elif prop_type == PropertyType.RELATION:
            return await self.get_values_of_relation_property(property_name)

        elif prop_type == PropertyType.MULTI_SELECT:
            return self.get_values_of_multiselect_property(property_name)

        elif prop_type == PropertyType.SELECT:
            return self.get_value_of_select_property(property_name)

        elif prop_type == PropertyType.URL:
            return self.get_value_of_url_property(property_name)

        elif prop_type == PropertyType.NUMBER:
            return self.get_value_of_number_property(property_name)

        elif prop_type == PropertyType.CHECKBOX:
            return self.get_value_of_checkbox_property(property_name)

        elif prop_type == PropertyType.DATE:
            return self.get_value_of_date_property(property_name)

        elif prop_type == PropertyType.TITLE:
            return await self.get_value_of_title_property(property_name)

        elif prop_type == PropertyType.RICH_TEXT:
            return await self.get_value_of_rich_text_property(property_name)

        elif prop_type == PropertyType.EMAIL:
            return self.get_value_of_email_property(property_name)

        elif prop_type == PropertyType.PHONE_NUMBER:
            return self.get_value_of_phone_number_property(property_name)

        elif prop_type == PropertyType.PEOPLE:
            return await self.get_values_of_people_property(property_name)

        elif prop_type == PropertyType.CREATED_TIME:
            return self.get_value_of_created_time_property(property_name)

    def get_value_of_status_property(self, name: str) -> str | None:
        """Get the status value by property name."""
        status_property = self._get_property(name, PageStatusProperty)
        if not status_property or not status_property.status:
            return None
        return status_property.status.name

    def get_value_of_select_property(self, name: str) -> str | None:
        """Get the select value by property name."""
        select_property = self._get_property(name, PageSelectProperty)
        if not select_property or not select_property.select:
            return None
        return select_property.select.name

    async def get_value_of_title_property(self, name: str) -> str:
        """Get formatted title value by property name."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        title_property = self._get_property(name, PageTitleProperty)
        if not title_property:
            return ""
        return await TextInlineFormatter.extract_text_with_formatting(title_property)

    async def get_values_of_people_property(self, name: str) -> list[dict[str, Any]]:
        """Get people values by property name."""
        people_property = self._get_property(name, PagePeopleProperty)
        if not people_property:
            return []
        return people_property.people

    def get_value_of_created_time_property(self, name: str) -> str | None:
        """Get created time value by property name."""
        prop = self._properties.get(name)
        if not prop:
            return None
        if isinstance(prop, dict):
            return prop.get("created_time")
        # For CREATED_TIME there might not be a specific property class yet
        return getattr(prop, "created_time", None)

    async def get_values_of_relation_property(self, name: str) -> list[str]:
        """Get relation page titles by property name."""
        relation_property = self._get_property(name, PageRelationProperty)
        if not relation_property:
            return []
        return await self._get_relation_property_values_from_typed(relation_property)

    def get_values_of_multiselect_property(self, name: str) -> list[str]:
        """Get multiselect option names by property name."""
        multiselect_property = self._get_property(name, PageMultiSelectProperty)
        if not multiselect_property:
            return []
        return [option.name for option in multiselect_property.multi_select]

    def get_value_of_url_property(self, name: str) -> str | None:
        """Get URL value by property name."""
        url_property = self._get_property(name, PageURLProperty)
        return url_property.url if url_property else None

    def get_value_of_number_property(self, name: str) -> float | None:
        """Get number value by property name."""
        number_property = self._get_property(name, PageNumberProperty)
        return number_property.number if number_property else None

    def get_value_of_checkbox_property(self, name: str) -> bool:
        """Get checkbox value by property name."""
        checkbox_property = self._get_property(name, PageCheckboxProperty)
        return checkbox_property.checkbox if checkbox_property else False

    def get_value_of_date_property(self, name: str) -> str | None:
        """Get date start value by property name."""
        date_property = self._get_property(name, PageDateProperty)
        if not date_property or not date_property.date:
            return None
        return date_property.date.start

    async def get_value_of_rich_text_property(self, name: str) -> str:
        """Get formatted rich text value by property name."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        rich_text_property = self._get_property(name, PageRichTextProperty)
        if not rich_text_property:
            return ""
        return await TextInlineFormatter.extract_text_with_formatting(
            rich_text_property
        )

    def get_value_of_email_property(self, name: str) -> str | None:
        """Get email value by property name."""
        email_property = self._get_property(name, PageEmailProperty)
        return email_property.email if email_property else None

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        """Get phone number value by property name."""
        phone_property = self._get_property(name, PagePhoneNumberProperty)
        return phone_property.phone_number if phone_property else None

    def get_value_of_status_property(self, property_name: str) -> str | None:
        """Get the name of a status property."""
        status_prop = self._get_property(property_name, PageStatusProperty)
        return status_prop.status.name if status_prop and status_prop.status else None

    def get_value_of_mulitselect_property(self, property_name: str) -> list[str]:
        """Get the names of selected options in a multiselect property."""
        multiselect_prop = self._get_property(property_name, PageMultiSelectProperty)
        if multiselect_prop:
            return [option.name for option in multiselect_prop.multi_select]
        return []

    async def get_rich_text_plain(self, property_name: str) -> str:
        """Get the plain text of a rich text property."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        rich_text_prop = self._get_property(property_name, PageRichTextProperty)
        return await TextInlineFormatter.extract_text_with_formatting(rich_text_prop)

    # ===== PROPERTY SETTER METHODS =====

    async def set_title_property_by_name(self, title: str) -> str:
        """Set the page title property."""
        await self._page_client.patch_title(title)
        self._title = title
        return title

    async def set_rich_text_property_by_name(
        self, property_name: str, text: str
    ) -> str:
        """Set a rich text property value by property name."""
        await self._page_client.patch_rich_text_property(property_name, text)
        return text

    async def set_url_property_by_name(self, property_name: str, url: str) -> str:
        """Set a URL property value by property name."""
        await self._page_client.patch_url_property(property_name, url)
        return url

    async def set_email_property_by_name(self, property_name: str, email: str) -> str:
        """Set an email property value by property name."""
        await self._page_client.patch_email_property(property_name, email)
        return email

    async def set_phone_number_property_by_name(
        self, property_name: str, phone: str
    ) -> str:
        """Set a phone number property value by property name."""
        await self._page_client.patch_phone_property(property_name, phone)
        return phone

    async def set_number_property_by_name(
        self, property_name: str, number: Union[int, float]
    ) -> Union[int, float]:
        """Set a number property value by property name."""
        await self._page_client.patch_number_property(property_name, number)
        return number

    async def set_checkbox_property_by_name(
        self, property_name: str, checked: bool
    ) -> bool:
        """Set a checkbox property value by property name."""
        await self._page_client.patch_checkbox_property(property_name, checked)
        return checked

    async def set_select_property_by_name(
        self, property_name: str, option_name: str
    ) -> str:
        """Set a select property value by property name."""
        await self._page_client.patch_select_property(property_name, option_name)
        return option_name

    async def set_multi_select_property_by_name(
        self, property_name: str, option_names: list[str]
    ) -> list[str]:
        """Set a multi-select property value by property name."""
        await self._page_client.patch_multi_select_property(property_name, option_names)
        return option_names

    async def set_date_property_by_name(
        self, property_name: str, date_value: Union[str, dict]
    ) -> Union[str, dict]:
        """Set a date property value by property name."""
        await self._page_client.patch_date_property(property_name, date_value)
        return date_value

    async def set_status_property_by_name(
        self, property_name: str, status_name: str
    ) -> str:
        """Set a status property value by property name."""
        await self._page_client.patch_status_property(property_name, status_name)
        return status_name

    async def set_relation_property_by_name(
        self, property_name: str, relation_ids: Union[str, list[str]]
    ) -> Union[str, list[str]]:
        """Set a relation property value by property name."""
        await self._page_client.patch_relation_property(property_name, relation_ids)
        return relation_ids

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        """
        Get the available options for a property (select, multi_select, status, relation).
        Returns empty list if property doesn't exist or has no options.
        """
        if property_name not in self._properties:
            return []

        if self._parent_database:
            return await self._parent_database.get_options_by_property_name(
                property_name
            )

        return []

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        """
        Set the value of a specific property by its name using typed methods.
        Returns the set value or None if property doesn't exist.
        """
        if property_name not in self._properties:
            return None

        prop = self._properties.get(property_name)
        if not prop:
            return None

        # Handle dict properties (fallback)
        if isinstance(prop, dict):
            prop_type = prop.get("type")
        else:
            prop_type = prop.type

        # Route to specific typed setter methods
        if prop_type == PropertyType.TITLE:
            return await self.set_title_property_by_name(str(value))
        elif prop_type == PropertyType.RICH_TEXT:
            return await self.set_rich_text_property_by_name(property_name, str(value))
        elif prop_type == PropertyType.URL:
            return await self.set_url_property_by_name(property_name, str(value))
        elif prop_type == PropertyType.EMAIL:
            return await self.set_email_property_by_name(property_name, str(value))
        elif prop_type == PropertyType.PHONE_NUMBER:
            return await self.set_phone_number_property_by_name(
                property_name, str(value)
            )
        elif prop_type == PropertyType.NUMBER:
            return await self.set_number_property_by_name(property_name, float(value))
        elif prop_type == PropertyType.CHECKBOX:
            return await self.set_checkbox_property_by_name(property_name, bool(value))
        elif prop_type == PropertyType.SELECT:
            return await self.set_select_property_by_name(property_name, str(value))
        elif prop_type == PropertyType.MULTI_SELECT:
            return await self.set_multi_select_property_by_name(
                property_name, list(value)
            )
        elif prop_type == PropertyType.DATE:
            return await self.set_date_property_by_name(property_name, value)
        elif prop_type == PropertyType.STATUS:
            return await self.set_status_property_by_name(property_name, str(value))
        elif prop_type == PropertyType.RELATION:
            return await self.set_relation_property_by_name(property_name, value)

        return None

    async def set_relation_property_values_by_name(
        self, property_name: str, page_titles: list[str]
    ) -> list[str]:
        """
        Add one or more relations to a relation property using page titles.
        Returns the relation IDs if successful, empty list otherwise.
        """
        if not self._parent_database:
            return []

        property_type = self._parent_database.get_property_type(property_name)
        if property_type != PropertyType.RELATION:
            return []

        page_ids = await self.convert_page_titles_to_ids(page_titles)
        return await self.set_relation_property_by_name(property_name, page_ids)

    async def convert_page_titles_to_ids(self, page_titles: list[str]) -> list[str]:
        """
        Convert a list of page titles to page IDs using parallel processing.
        """
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
        """Get relation values from typed RelationProperty."""
        relation_page_ids = [rel.id for rel in relation_prop.relation]

        notion_pages = [
            await load_page_from_id(page_id) for page_id in relation_page_ids
        ]
        return [page.title for page in notion_pages if page]

    def _extract_property_value_fallback(self, property_dict: dict) -> Any:
        """Fallback für unbekannte Property-Typen."""
        property_type = property_dict.get("type")
        return property_dict.get(property_type)

    def _setup_page_context_provider(self) -> PageContextProvider:
        return PageContextProvider(
            page_id=self._page_id,
            database_client=NotionDatabseHttpClient(token=self._page_client.token),
            file_upload_client=FileUploadHttpClient(),
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
