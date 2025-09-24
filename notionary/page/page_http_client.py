from typing import Any

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto, NotionPageUpdateDto
from notionary.page.properties.page_property_models import (
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PagePropertyT,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
    RelationItem,
    SelectOption,
    StatusOption,
)
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.file_models import ExternalFile
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon


class NotionPageHttpClient(NotionHttpClient):
    def __init__(
        self,
        page_id: str,
        properties: dict[str, PageProperty] | None = None,
    ):
        super().__init__()
        self._page_id = page_id
        self._page_properties = properties

    async def get_page(self) -> NotionPageDto:
        response = await self.get(f"pages/{self._page_id}")
        page_dto = NotionPageDto.model_validate(response)
        return page_dto

    async def patch_page(self, data: BaseModel) -> NotionPageDto:
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        result_dict = await self.patch(f"pages/{self._page_id}", data=data_dict)
        page_update_result = NotionPageDto.model_validate(result_dict)
        self._page_properties = page_update_result.properties
        return page_update_result

    async def patch_emoji_icon(self, emoji: str) -> NotionPageDto:
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionPageUpdateDto(icon=icon)
        return await self.patch_page(update_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionPageDto:
        external_file = ExternalFile(url=icon_url)
        icon = ExternalIcon(external=external_file)
        update_dto = NotionPageUpdateDto(icon=icon)
        return await self.patch_page(update_dto)

    async def remove_icon(self) -> NotionPageDto:
        update_dto = NotionPageUpdateDto(icon=None)
        return await self.patch_page(update_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionPageDto:
        cover = NotionCover.from_url(cover_url)
        update_dto = NotionPageUpdateDto(cover=cover)
        return await self.patch_page(update_dto)

    async def remove_cover(self) -> NotionPageDto:
        update_dto = NotionPageUpdateDto(cover=None)
        return await self.patch_page(update_dto)

    async def archive_page(self) -> NotionPageDto:
        update_dto = NotionPageUpdateDto(archived=True)
        return await self.patch_page(update_dto)

    async def unarchive_page(self) -> NotionPageDto:
        update_dto = NotionPageUpdateDto(archived=False)
        return await self.patch_page(update_dto)

    async def patch_property(self, property_name: str, value: Any, property_type: type[PagePropertyT]) -> NotionPageDto:
        """
        Updates a single property using the property type and internal schema.
        """
        # Get the current property to understand its type
        current_property = self._get_typed_property(property_name, property_type)

        # Update the internal schema with the new value
        if not self._page_properties:
            self._page_properties = {}

        # Create a new property instance with the updated value
        updated_property = self._create_updated_property(property_type, current_property, value)

        self._page_properties[property_name] = updated_property

        properties = {property_name: updated_property}
        update_dto = NotionPageUpdateDto(properties=properties)

        return await self.patch_page(update_dto)

    async def patch_title(self, title: str) -> NotionPageDto:
        return await self.patch_property("title", title, PageTitleProperty)

    async def patch_rich_text_property(self, property_name: str, text: str) -> NotionPageDto:
        return await self.patch_property(property_name, text, PageRichTextProperty)

    async def patch_url_property(self, property_name: str, url: str) -> NotionPageDto:
        return await self.patch_property(property_name, url, PageURLProperty)

    async def patch_email_property(self, property_name: str, email: str) -> NotionPageDto:
        return await self.patch_property(property_name, email, PageEmailProperty)

    async def patch_phone_property(self, property_name: str, phone: str) -> NotionPageDto:
        return await self.patch_property(property_name, phone, PagePhoneNumberProperty)

    async def patch_number_property(self, property_name: str, number: int | float) -> NotionPageDto:
        return await self.patch_property(property_name, number, PageNumberProperty)

    async def patch_checkbox_property(self, property_name: str, checked: bool) -> NotionPageDto:
        return await self.patch_property(property_name, checked, PageCheckboxProperty)

    async def patch_select_property(self, property_name: str, option_name: str) -> NotionPageDto:
        return await self.patch_property(property_name, option_name, PageSelectProperty)

    async def patch_multi_select_property(self, property_name: str, option_names: list[str]) -> NotionPageDto:
        return await self.patch_property(property_name, option_names, PageMultiSelectProperty)

    async def patch_date_property(self, property_name: str, date_value: str | dict) -> NotionPageDto:
        return await self.patch_property(property_name, date_value, PageDateProperty)

    async def patch_status_property(self, property_name: str, status_name: str) -> NotionPageDto:
        return await self.patch_property(property_name, status_name, PageStatusProperty)

    async def patch_relation_property(self, property_name: str, relation_ids: str | list[str]) -> NotionPageDto:
        if isinstance(relation_ids, str):
            relation_ids = [relation_ids]
        return await self.patch_property(property_name, relation_ids, PageRelationProperty)

    def _create_updated_property(
        self,
        property_type: type[PagePropertyT],
        current_property: PagePropertyT | None,
        value: Any,
    ) -> PagePropertyT:
        """
        Creates an updated property instance based on the property type and new value.
        """
        # Get the property ID from the current property if it exists
        property_id = current_property.id if current_property else ""

        if property_type == PageTitleProperty:
            return PageTitleProperty(
                id=property_id,
                title=[RichTextObject(type="text", text={"content": str(value)})],
            )
        elif property_type == PageRichTextProperty:
            return PageRichTextProperty(
                id=property_id,
                rich_text=[RichTextObject(type="text", text={"content": str(value)})],
            )
        elif property_type == PageURLProperty:
            return PageURLProperty(id=property_id, url=str(value))
        elif property_type == PageEmailProperty:
            return PageEmailProperty(id=property_id, email=str(value))
        elif property_type == PagePhoneNumberProperty:
            return PagePhoneNumberProperty(id=property_id, phone_number=str(value))
        elif property_type == PageNumberProperty:
            return PageNumberProperty(id=property_id, number=float(value))
        elif property_type == PageCheckboxProperty:
            return PageCheckboxProperty(id=property_id, checkbox=bool(value))
        elif property_type == PageSelectProperty:
            select_option = SelectOption(id="", name=str(value))
            return PageSelectProperty(id=property_id, select=select_option)
        elif property_type == PageMultiSelectProperty:
            multi_select_options = [SelectOption(id="", name=str(item)) for item in value]
            return PageMultiSelectProperty(id=property_id, multi_select=multi_select_options)
        elif property_type == PageDateProperty:
            if isinstance(value, dict) and "start" in value:
                date_value = DateValue(**value)
            else:
                date_value = DateValue(start=str(value))
            return PageDateProperty(id=property_id, date=date_value)
        elif property_type == PageStatusProperty:
            status_option = StatusOption(id="", name=str(value))
            return PageStatusProperty(id=property_id, status=status_option)
        elif property_type == PageRelationProperty:
            relation_items = [RelationItem(id=str(item)) for item in value]
            return PageRelationProperty(id=property_id, relation=relation_items)
        else:
            raise ValueError(f"Unsupported property type: {property_type}")

    def _get_typed_property(self, name: str, property_type: type[PagePropertyT]) -> PagePropertyT | None:
        """Get a property by name and type with type safety."""
        if not self._page_properties:
            return None

        prop = self._page_properties.get(name)

        if isinstance(prop, property_type):
            return prop
        return None

    def get_typed_property(self, property_name: str, property_type: type[PagePropertyT]) -> PagePropertyT | None:
        return self._get_typed_property(property_name, property_type)
