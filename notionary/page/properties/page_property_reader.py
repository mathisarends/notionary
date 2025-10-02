from __future__ import annotations

import difflib
import inspect
from typing import TYPE_CHECKING, ClassVar, Never

from notionary.blocks.rich_text.rich_text_markdown_converter import convert_rich_text_to_markdown
from notionary.data_source.service import NotionDataSource
from notionary.page.properties.exceptions import (
    AccessPagePropertyWithoutDataSourceError,
    PagePropertyNotFoundError,
    PagePropertyTypeError,
)
from notionary.page.properties.page_property_models import (
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePeopleProperty,
    PagePhoneNumberProperty,
    PagePropertyT,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
)

if TYPE_CHECKING:
    from notionary import NotionPage


class PagePropertyReader:
    _PROPERTY_TYPE_TO_METHOD_MAP: ClassVar[dict[type, str]] = {
        PageStatusProperty: "get_value_of_status_property",
        PageSelectProperty: "get_value_of_select_property",
        PageTitleProperty: "get_value_of_title_property",
        PagePeopleProperty: "get_values_of_people_property",
        PageCreatedTimeProperty: "get_value_of_created_time_property",
        PageRelationProperty: "get_values_of_relation_property",
        PageMultiSelectProperty: "get_values_of_multiselect_property",
        PageURLProperty: "get_value_of_url_property",
        PageNumberProperty: "get_value_of_number_property",
        PageCheckboxProperty: "get_value_of_checkbox_property",
        PageDateProperty: "get_value_of_date_property",
        PageRichTextProperty: "get_value_of_rich_text_property",
        PageEmailProperty: "get_value_of_email_property",
        PagePhoneNumberProperty: "get_value_of_phone_number_property",
    }

    def __init__(self, page: NotionPage) -> None:
        self._properties = page.properties
        self._parent_data_source = page.parent_data_source
        self._parent_type = page.parent_type
        self._page_url = page.url

    def get_value_of_status_property(self, name: str) -> str | None:
        status_property = self._get_typed_property_or_raise(name, PageStatusProperty)
        if not status_property.status:
            return None
        return status_property.status.name

    def get_value_of_select_property(self, name: str) -> str | None:
        select_property = self._get_typed_property_or_raise(name, PageSelectProperty)
        if not select_property.select:
            return None
        return select_property.select.name

    async def get_value_of_title_property(self, name: str) -> str:
        title_property = self._get_typed_property_or_raise(name, PageTitleProperty)
        return await convert_rich_text_to_markdown(title_property.title)

    def get_values_of_people_property(self, property_name: str) -> list[str]:
        people_prop = self._get_typed_property_or_raise(property_name, PagePeopleProperty)
        names = [person.name for person in people_prop.people if person.name]
        return names

    def get_value_of_created_time_property(self, name: str) -> str | None:
        created_time_property = self._get_typed_property_or_raise(name, PageCreatedTimeProperty)
        return created_time_property.created_time

    async def get_values_of_relation_property(self, name: str) -> list[str]:
        from notionary.page.factory import load_page_from_id

        relation_property = self._get_typed_property_or_raise(name, PageRelationProperty)
        relation_page_ids = [rel.id for rel in relation_property.relation]
        notion_pages = [await load_page_from_id(page_id) for page_id in relation_page_ids]
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
        if not date_property.date:
            return None
        return date_property.date.start

    async def get_value_of_rich_text_property(self, name: str) -> str:
        rich_text_property = self._get_typed_property_or_raise(name, PageRichTextProperty)
        return await convert_rich_text_to_markdown(rich_text_property.rich_text)

    def get_value_of_email_property(self, name: str) -> str | None:
        email_property = self._get_typed_property_or_raise(name, PageEmailProperty)
        return email_property.email

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        phone_property = self._get_typed_property_or_raise(name, PagePhoneNumberProperty)
        return phone_property.phone_number

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = self._get_parent_data_source_or_raise()
        return data_source.get_select_options_by_property_name(property_name)

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = self._get_parent_data_source_or_raise()
        return data_source.get_multi_select_options_by_property_name(property_name)

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = self._get_parent_data_source_or_raise()
        return data_source.get_status_options_by_property_name(property_name)

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        data_source = self._get_parent_data_source_or_raise()
        return await data_source.get_relation_options_by_property_name(property_name)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        data_source = self._get_parent_data_source_or_raise()
        return await data_source.get_options_for_property_by_name(property_name)

    def _get_parent_data_source_or_raise(self) -> NotionDataSource:
        if not self._parent_data_source:
            raise AccessPagePropertyWithoutDataSourceError(self._parent_type)
        return self._parent_data_source

    def _get_typed_property_or_raise(self, name: str, property_type: type[PagePropertyT]) -> PagePropertyT:
        prop = self._properties.get(name)

        if prop is None:
            self._handle_prop_not_found(name)

        is_incorrect_type = not isinstance(prop, property_type)
        if is_incorrect_type:
            self._handle_incorrect_type(name, type(prop))
        return prop

    def _handle_prop_not_found(self, name: str) -> Never:
        if self._parent_data_source is None:
            raise AccessPagePropertyWithoutDataSourceError(self._parent_type)

        suggestions = self._find_closest_property_names(name)
        raise PagePropertyNotFoundError(property_name=name, page_url=self._page_url, suggestions=suggestions)

    def _find_closest_property_names(self, property_name: str, max_matches: int = 3) -> list[str]:
        if not self._properties:
            return []

        all_names = list(self._properties.keys())
        return difflib.get_close_matches(property_name, all_names, n=max_matches, cutoff=0.6)

    def _handle_incorrect_type(self, property_name: str, actual_type: type) -> Never:
        used_method = None
        current_frame = inspect.currentframe()

        internal_caller_frame = current_frame.f_back
        public_method_frame = internal_caller_frame.f_back if internal_caller_frame else None
        if current_frame and public_method_frame:
            original_caller_frame = current_frame.f_back.f_back
            used_method = original_caller_frame.f_code.co_name

        correct_method = self._PROPERTY_TYPE_TO_METHOD_MAP.get(actual_type)

        raise PagePropertyTypeError(
            property_name=property_name,
            actual_type=actual_type.__name__,
            used_method=used_method,
            correct_method=correct_method,
        )
