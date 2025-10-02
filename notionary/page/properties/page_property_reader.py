from __future__ import annotations

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.data_source import NotionDataSource
from notionary.page.properties.page_property_models import (
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


class PagePropertyReader:
    def __init__(self, properties: dict[str, PageProperty], parent_data_source: NotionDataSource | None) -> None:
        self._properties = properties
        self._parent_data_source = parent_data_source

    @property
    def data_source_reader(self) -> NotionDataSource | None:
        return self._parent_data_source

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
        from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter

        title_property = self._get_property(name, PageTitleProperty)
        if not title_property:
            return ""
        converter = RichTextToMarkdownConverter()
        return await converter.to_markdown(title_property.title)

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
        from notionary.page.factory import load_page_from_id

        relation_property = self._get_property(name, PageRelationProperty)
        if not relation_property:
            return []

        relation_page_ids = [rel.id for rel in relation_property.relation]
        notion_pages = [await load_page_from_id(page_id) for page_id in relation_page_ids]
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
        rich_text_property = self._get_property(name, PageRichTextProperty)
        if not rich_text_property:
            return ""

        converter = RichTextToMarkdownConverter()
        return await converter.to_markdown(rich_text_property.rich_text)

    def get_value_of_email_property(self, name: str) -> str | None:
        email_property = self._get_property(name, PageEmailProperty)
        return email_property.email if email_property else None

    def get_value_of_phone_number_property(self, name: str) -> str | None:
        phone_property = self._get_property(name, PagePhoneNumberProperty)
        return phone_property.phone_number if phone_property else None

    def _get_property(self, name: str, property_type: type[PagePropertyT]) -> PagePropertyT | None:
        prop = self._properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        return (
            self.data_source_reader.get_select_options_by_property_name(property_name)
            if self.data_source_reader
            else []
        )

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[str]:
        return (
            self.data_source_reader.get_multi_select_options_by_property_name(property_name)
            if self.data_source_reader
            else []
        )

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        return (
            self.data_source_reader.get_status_options_by_property_name(property_name)
            if self.data_source_reader
            else []
        )

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        return (
            await self.data_source_reader.get_relation_options_by_property_name(property_name)
            if self.data_source_reader
            else []
        )

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        return (
            await self.data_source_reader.get_options_for_property_by_name(property_name)
            if self.data_source_reader
            else []
        )
