from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Never

from notionary.blocks.rich_text.rich_text_markdown_converter import convert_rich_text_to_markdown
from notionary.exceptions.properties import (
    AccessPagePropertyWithoutDataSourceError,
    PagePropertyNotFoundError,
    PagePropertyTypeError,
)
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.models import (
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePeopleProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PagePropertyT,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
)
from notionary.shared.models.parent import ParentType

if TYPE_CHECKING:
    from notionary import NotionDataSource


class PagePropertyHandler:
    def __init__(
        self,
        properties: dict[str, PageProperty],
        parent_type: ParentType,
        page_url: str,
        page_property_http_client: PagePropertyHttpClient,
        parent_data_source: str,
    ) -> None:
        self._properties = properties
        self._parent_type = parent_type
        self._page_url = page_url
        self._property_http_client = page_property_http_client
        self._parent_data_source_id = parent_data_source
        self._parent_data_source: NotionDataSource | None = None
        self._data_source_loaded = False

    # =========================================================================
    # Reader Methods
    # =========================================================================

    def get_value_of_status_property(self, name: str) -> str | None:
        status_property = self._get_typed_property_or_raise(name, PageStatusProperty)
        return status_property.status.name if status_property.status else None

    def get_value_of_select_property(self, name: str) -> str | None:
        select_property = self._get_typed_property_or_raise(name, PageSelectProperty)
        return select_property.select.name if select_property.select else None

    async def get_value_of_title_property(self, name: str) -> str:
        title_property = self._get_typed_property_or_raise(name, PageTitleProperty)
        return await convert_rich_text_to_markdown(title_property.title)

    def get_values_of_people_property(self, property_name: str) -> list[str]:
        people_prop = self._get_typed_property_or_raise(property_name, PagePeopleProperty)
        return [person.name for person in people_prop.people if person.name]

    def get_value_of_created_time_property(self, name: str) -> str | None:
        created_time_property = self._get_typed_property_or_raise(name, PageCreatedTimeProperty)
        return created_time_property.created_time

    async def get_values_of_relation_property(self, name: str) -> list[str]:
        from notionary import NotionPage

        relation_property = self._get_typed_property_or_raise(name, PageRelationProperty)
        relation_page_ids = [rel.id for rel in relation_property.relation]
        notion_pages = [await NotionPage.from_id(page_id) for page_id in relation_page_ids]
        return [page.title for page in notion_pages if page]

    def get_values_of_multiselect_property(self, name: str) -> list[str]:
        multiselect_property = self._get_typed_property_or_raise(name, PageMultiSelectProperty)
        return [option.name for option in multiselect_property.multi_select]

    def get_value_of_url_property(self, name: str) -> str | None:
        url_property = self._get_typed_property_or_raise(name, PageURLProperty)
        return url_property.url

    def get_value_of_number_property(self, name: str) -> float | None:
        number_property = self._get_typed_property_or_raise(name, PageNumberProperty)
        return number_property.number

    def get_value_of_checkbox_property(self, name: str) -> bool:
        checkbox_property = self._get_typed_property_or_raise(name, PageCheckboxProperty)
        return checkbox_property.checkbox

    def get_value_of_date_property(self, name: str) -> str | None:
        date_property = self._get_typed_property_or_raise(name, PageDateProperty)
        return date_property.date.start if date_property.date else None

    async def get_value_of_rich_text_property(self, name: str) -> str:
        rich_text_property = self._get_typed_property_or_raise(name, PageRichTextProperty)
        return await convert_rich_text_to_markdown(rich_text_property.rich_text)

    def get_value_of_email_property(self, name: str) -> str | None:
        email_property = self._get_typed_property_or_raise(name, PageEmailProperty)
        return email_property.email

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        phone_property = self._get_typed_property_or_raise(name, PagePhoneNumberProperty)
        return phone_property.phone_number

    # =========================================================================
    # Options Getters
    # =========================================================================

    async def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = await self._get_parent_data_source_or_raise()
        return data_source.get_select_options_by_property_name(property_name)

    async def get_multi_select_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = await self._get_parent_data_source_or_raise()
        return data_source.get_multi_select_options_by_property_name(property_name)

    async def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = await self._get_parent_data_source_or_raise()
        return data_source.get_status_options_by_property_name(property_name)

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = await self._get_parent_data_source_or_raise()
        return await data_source.get_relation_options_by_property_name(property_name)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        data_source = await self._get_parent_data_source_or_raise()
        return await data_source.get_options_for_property_by_name(property_name)

    async def get_schema_description(self, property_name: str) -> str:
        data_source = await self._get_parent_data_source_or_raise()
        return await data_source.get_schema_description(property_name)

    # =========================================================================
    # Writer Methods
    # =========================================================================

    async def set_title_property(self, property_name: str, title: str) -> None:
        self._get_typed_property_or_raise(property_name, PageTitleProperty)
        updated_page = await self._property_http_client.patch_title(property_name, title)
        self._properties = updated_page.properties

    async def set_rich_text_property(self, property_name: str, text: str) -> None:
        self._get_typed_property_or_raise(property_name, PageRichTextProperty)
        updated_page = await self._property_http_client.patch_rich_text_property(property_name, text)
        self._properties = updated_page.properties

    async def set_url_property(self, property_name: str, url: str) -> None:
        self._get_typed_property_or_raise(property_name, PageURLProperty)
        updated_page = await self._property_http_client.patch_url_property(property_name, url)
        self._properties = updated_page.properties

    async def set_email_property(self, property_name: str, email: str) -> None:
        self._get_typed_property_or_raise(property_name, PageEmailProperty)
        updated_page = await self._property_http_client.patch_email_property(property_name, email)
        self._properties = updated_page.properties

    async def set_phone_number_property(self, property_name: str, phone_number: str) -> None:
        self._get_typed_property_or_raise(property_name, PagePhoneNumberProperty)
        updated_page = await self._property_http_client.patch_phone_property(property_name, phone_number)
        self._properties = updated_page.properties

    async def set_number_property(self, property_name: str, number: int | float) -> None:
        self._get_typed_property_or_raise(property_name, PageNumberProperty)
        updated_page = await self._property_http_client.patch_number_property(property_name, number)
        self._properties = updated_page.properties

    async def set_checkbox_property(self, property_name: str, checked: bool) -> None:
        self._get_typed_property_or_raise(property_name, PageCheckboxProperty)
        updated_page = await self._property_http_client.patch_checkbox_property(property_name, checked)
        self._properties = updated_page.properties

    async def set_date_property(self, property_name: str, date_value: str | dict) -> None:
        self._get_typed_property_or_raise(property_name, PageDateProperty)
        updated_page = await self._property_http_client.patch_date_property(property_name, date_value)
        self._properties = updated_page.properties

    async def set_select_property_by_option_name(self, property_name: str, option_name: str) -> None:
        self._get_typed_property_or_raise(property_name, PageSelectProperty)
        updated_page = await self._property_http_client.patch_select_property(property_name, option_name)
        self._properties = updated_page.properties

    async def set_multi_select_property_by_option_names(self, property_name: str, option_names: list[str]) -> None:
        self._get_typed_property_or_raise(property_name, PageMultiSelectProperty)
        updated_page = await self._property_http_client.patch_multi_select_property(property_name, option_names)
        self._properties = updated_page.properties

    async def set_status_property_by_option_name(self, property_name: str, status: str) -> None:
        self._get_typed_property_or_raise(property_name, PageStatusProperty)
        updated_page = await self._property_http_client.patch_status_property(property_name, status)
        self._properties = updated_page.properties

    async def set_relation_property_by_page_titles(self, property_name: str, page_titles: list[str]) -> None:
        self._get_typed_property_or_raise(property_name, PageRelationProperty)
        relation_ids = await self._convert_page_titles_to_ids(page_titles)
        updated_page = await self._property_http_client.patch_relation_property(property_name, relation_ids)
        self._properties = updated_page.properties

    async def _ensure_data_source_loaded(self) -> None:
        from notionary import NotionDataSource

        if self._data_source_loaded:
            return

        self._parent_data_source = (
            await NotionDataSource.from_id(self._parent_data_source_id) if self._parent_data_source_id else None
        )
        self._data_source_loaded = True

    async def _get_parent_data_source_or_raise(self) -> NotionDataSource:
        await self._ensure_data_source_loaded()

        if not self._parent_data_source:
            raise AccessPagePropertyWithoutDataSourceError(self._parent_type)
        return self._parent_data_source

    def _get_typed_property_or_raise(self, name: str, property_type: type[PagePropertyT]) -> PagePropertyT:
        prop = self._properties.get(name)

        if prop is None:
            self._handle_prop_not_found(name)

        if not isinstance(prop, property_type):
            self._handle_incorrect_type(name, type(prop))

        return prop

    def _handle_prop_not_found(self, name: str) -> Never:
        raise PagePropertyNotFoundError(
            property_name=name,
            page_url=self._page_url,
            available_properties=list(self._properties.keys()),
        )

    def _handle_incorrect_type(self, property_name: str, actual_type: type) -> Never:
        raise PagePropertyTypeError(
            property_name=property_name,
            actual_type=actual_type.__name__,
        )

    async def _convert_page_titles_to_ids(self, page_titles: list[str]) -> list[str]:
        from notionary import NotionPage

        if not page_titles:
            return []

        pages = await asyncio.gather(*[NotionPage.from_title(title=title) for title in page_titles])

        return [page.id for page in pages if page]
