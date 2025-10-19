from typing import Any

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.http.client import NotionHttpClient
from notionary.page.properties.models import (
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
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
from notionary.page.schemas import NotionPageDto, PgePropertiesUpdateDto


class PagePropertyHttpClient(NotionHttpClient):
    def __init__(self, page_id: str) -> None:
        super().__init__()
        self._page_id = page_id

    async def patch_page(self, data: BaseModel) -> NotionPageDto:
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)

        result_dict = await self.patch(f"pages/{self._page_id}", data=data_dict)
        return NotionPageDto.model_validate(result_dict)

    async def _patch_property(
        self,
        property_name: str,
        value: Any,
        property_type: type[PagePropertyT],
        current_property: PagePropertyT | None = None,
    ) -> NotionPageDto:
        updated_property = self._create_updated_property(property_type, current_property, value)

        properties = {property_name: updated_property}
        update_dto = PgePropertiesUpdateDto(properties=properties)

        return await self.patch_page(update_dto)

    async def patch_title(self, property_name: str, title: str) -> NotionPageDto:
        return await self._patch_property(property_name, title, PageTitleProperty)

    async def patch_rich_text_property(self, property_name: str, text: str) -> NotionPageDto:
        return await self._patch_property(property_name, text, PageRichTextProperty)

    async def patch_url_property(self, property_name: str, url: str) -> NotionPageDto:
        return await self._patch_property(property_name, url, PageURLProperty)

    async def patch_email_property(self, property_name: str, email: str) -> NotionPageDto:
        return await self._patch_property(property_name, email, PageEmailProperty)

    async def patch_phone_property(self, property_name: str, phone: str) -> NotionPageDto:
        return await self._patch_property(property_name, phone, PagePhoneNumberProperty)

    async def patch_number_property(self, property_name: str, number: int | float) -> NotionPageDto:
        return await self._patch_property(property_name, number, PageNumberProperty)

    async def patch_checkbox_property(self, property_name: str, checked: bool) -> NotionPageDto:
        return await self._patch_property(property_name, checked, PageCheckboxProperty)

    async def patch_select_property(self, property_name: str, value: str) -> NotionPageDto:
        return await self._patch_property(property_name, value, PageSelectProperty)

    async def patch_multi_select_property(self, property_name: str, values: list[str]) -> NotionPageDto:
        return await self._patch_property(property_name, values, PageMultiSelectProperty)

    async def patch_date_property(self, property_name: str, date_value: str | dict) -> NotionPageDto:
        return await self._patch_property(property_name, date_value, PageDateProperty)

    async def patch_status_property(self, property_name: str, status: str) -> NotionPageDto:
        return await self._patch_property(property_name, status, PageStatusProperty)

    async def patch_relation_property(self, property_name: str, relation_ids: str | list[str]) -> NotionPageDto:
        if isinstance(relation_ids, str):
            relation_ids = [relation_ids]
        return await self._patch_property(property_name, relation_ids, PageRelationProperty)

    # TODO: Fix this shit here
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
                title=[RichText(type="text", text={"content": str(value)})],
            )
        elif property_type == PageRichTextProperty:
            return PageRichTextProperty(
                id=property_id,
                rich_text=[RichText(type="text", text={"content": str(value)})],
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
            select_option = SelectOption(name=str(value))
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
