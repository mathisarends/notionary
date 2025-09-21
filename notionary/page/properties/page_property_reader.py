from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

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
    PropertyType,
)

if TYPE_CHECKING:
    from notionary import NotionPage


Extractor = Callable[[str], Awaitable[Any]]


class PagePropertyReader:
    def __init__(self, notion_page: NotionPage):
        self._notion_page = notion_page
        self._property_extractors = self._build_property_extractors()

    def _build_property_extractors(self) -> dict[PropertyType, Extractor]:
        return {
            PropertyType.STATUS: lambda prop_name: self._await(
                self.get_value_of_status_property(prop_name)
            ),
            PropertyType.RELATION: self.get_values_of_relation_property,
            PropertyType.MULTI_SELECT: lambda prop_name: self._await(
                self.get_values_of_multiselect_property(prop_name)
            ),
            PropertyType.SELECT: lambda prop_name: self._await(
                self.get_value_of_select_property(prop_name)
            ),
            PropertyType.URL: lambda prop_name: self._await(
                self.get_value_of_url_property(prop_name)
            ),
            PropertyType.NUMBER: lambda prop_name: self._await(
                self.get_value_of_number_property(prop_name)
            ),
            PropertyType.CHECKBOX: lambda prop_name: self._await(
                self.get_value_of_checkbox_property(prop_name)
            ),
            PropertyType.DATE: lambda prop_name: self._await(
                self.get_value_of_date_property(prop_name)
            ),
            PropertyType.TITLE: self.get_value_of_title_property,
            PropertyType.RICH_TEXT: self.get_value_of_rich_text_property,
            PropertyType.EMAIL: lambda prop_name: self._await(
                self.get_value_of_email_property(prop_name)
            ),
            PropertyType.PHONE_NUMBER: lambda prop_name: self._await(
                self.get_value_of_phone_number_property(prop_name)
            ),
            PropertyType.PEOPLE: self.get_values_of_people_property,
            PropertyType.CREATED_TIME: lambda prop_name: self._await(
                self.get_value_of_created_time_property(prop_name)
            ),
        }

    @staticmethod
    def _await(value: Any) -> Awaitable[Any]:
        # Wrap sync results so they can always be awaited.
        # This ensures the caller can always use `await` without checks.
        return value if asyncio.iscoroutine(value) else asyncio.sleep(0, result=value)

    async def get_property_value_by_name(self, property_name: str) -> Any:
        prop = self._notion_page.properties.get(property_name)
        if not prop:
            return None

        if isinstance(prop, dict):
            return self._extract_property_value_fallback(prop)

        extractor = self._property_extractors.get(prop.type)
        if not extractor:
            return None

        return await extractor(property_name)

    def get_value_of_status_property(self, name: str) -> str | None:
        status_property = self._get_property(name, PageStatusProperty)
        if not status_property or not status_property.status:
            return None
        return status_property.status.name

    def get_value_of_select_property(self, name: str) -> str | None:
        select_property = self._get_property(name, PageSelectProperty)
        if not select_property or not select_property.select:
            return None
        return select_property.select.name

    async def get_value_of_title_property(self, name: str) -> str:
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        title_property = self._get_property(name, PageTitleProperty)
        if not title_property:
            return ""
        return await TextInlineFormatter.extract_text_with_formatting(title_property)

    def get_values_of_people_property(self, property_name: str) -> list[str]:
        people_prop = self._get_property(property_name, PagePeopleProperty)
        if not people_prop:
            return []

        names = [person.name for person in people_prop.people if person.name]
        return names

    def get_value_of_created_time_property(self, name: str) -> str | None:
        created_time_property = self._get_property(name, PageCreatedTimeProperty)
        return created_time_property.created_time if created_time_property else None

    async def get_values_of_relation_property(self, name: str) -> list[str]:
        """Get the values of a relation property."""
        from notionary.page.page_factory import load_page_from_id

        relation_property = self._get_property(name, PageRelationProperty)
        if not relation_property:
            return []

        relation_page_ids = [rel.id for rel in relation_property.relation]
        notion_pages = [
            await load_page_from_id(page_id) for page_id in relation_page_ids
        ]
        return [page.title for page in notion_pages if page]

    def get_values_of_multiselect_property(self, name: str) -> list[str]:
        multiselect_property = self._get_property(name, PageMultiSelectProperty)
        if not multiselect_property:
            return []
        return [option.name for option in multiselect_property.multi_select]

    def get_value_of_url_property(self, name: str) -> str | None:
        url_property = self._get_property(name, PageURLProperty)
        return url_property.url if url_property else None

    def get_value_of_number_property(self, name: str) -> float | None:
        number_property = self._get_property(name, PageNumberProperty)
        return number_property.number if number_property else None

    def get_value_of_checkbox_property(self, name: str) -> bool:
        checkbox_property = self._get_property(name, PageCheckboxProperty)
        return checkbox_property.checkbox if checkbox_property else False

    def get_value_of_date_property(self, name: str) -> str | None:
        date_property = self._get_property(name, PageDateProperty)
        if not date_property or not date_property.date:
            return None
        return date_property.date.start

    async def get_value_of_rich_text_property(self, name: str) -> str:
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        rich_text_property = self._get_property(name, PageRichTextProperty)
        if not rich_text_property:
            return ""

        return await TextInlineFormatter.extract_text_with_formatting(
            rich_text_property
        )

    def get_value_of_email_property(self, name: str) -> str | None:
        email_property = self._get_property(name, PageEmailProperty)
        return email_property.email if email_property else None

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        phone_property = self._get_property(name, PagePhoneNumberProperty)
        return phone_property.phone_number if phone_property else None

    def _extract_property_value_fallback(self, property_dict: dict) -> Any:
        property_type = property_dict.get("type")
        return property_dict.get(property_type)

    def _get_property(
        self, name: str, property_type: type[PagePropertyT]
    ) -> PagePropertyT | None:
        prop = self._notion_page.properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None
