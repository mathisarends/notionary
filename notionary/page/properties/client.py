from pydantic import BaseModel

from notionary.http.client import HttpClient
from notionary.page.properties.schemas import (
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
    PageProperty,
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
from notionary.page.schemas import PageDto, PgePropertiesUpdateDto
from notionary.rich_text.schemas import RichText


class PagePropertyHttpClient:
    def __init__(self, page_id: str, http: HttpClient) -> None:
        self._page_id = page_id
        self._http = http

    async def patch_page(self, data: BaseModel) -> PageDto:
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        result_dict = await self._http.patch(f"pages/{self._page_id}", data=data_dict)
        return PageDto.model_validate(result_dict)

    def _build_update(
        self, property_name: str, prop: PageProperty
    ) -> PgePropertiesUpdateDto:
        return PgePropertiesUpdateDto(properties={property_name: prop})

    async def patch_title(self, property_name: str, title: str) -> PageDto:
        update = self._build_update(
            property_name,
            PageTitleProperty(title=[RichText(type="text", text={"content": title})]),
        )
        return await self.patch_page(update)

    async def patch_rich_text_property(self, property_name: str, text: str) -> PageDto:
        update = self._build_update(
            property_name,
            PageRichTextProperty(
                rich_text=[RichText(type="text", text={"content": text})]
            ),
        )
        return await self.patch_page(update)

    async def patch_url_property(self, property_name: str, url: str) -> PageDto:
        update = self._build_update(property_name, PageURLProperty(url=url))
        return await self.patch_page(update)

    async def patch_email_property(self, property_name: str, email: str) -> PageDto:
        update = self._build_update(property_name, PageEmailProperty(email=email))
        return await self.patch_page(update)

    async def patch_phone_property(self, property_name: str, phone: str) -> PageDto:
        update = self._build_update(
            property_name, PagePhoneNumberProperty(phone_number=phone)
        )
        return await self.patch_page(update)

    async def patch_number_property(
        self, property_name: str, number: int | float
    ) -> PageDto:
        update = self._build_update(property_name, PageNumberProperty(number=number))
        return await self.patch_page(update)

    async def patch_checkbox_property(
        self, property_name: str, checked: bool
    ) -> PageDto:
        update = self._build_update(
            property_name, PageCheckboxProperty(checkbox=checked)
        )
        return await self.patch_page(update)

    async def patch_select_property(self, property_name: str, value: str) -> PageDto:
        update = self._build_update(
            property_name, PageSelectProperty(select=SelectOption(name=value))
        )
        return await self.patch_page(update)

    async def patch_multi_select_property(
        self, property_name: str, values: list[str]
    ) -> PageDto:
        update = self._build_update(
            property_name,
            PageMultiSelectProperty(
                multi_select=[SelectOption(name=v) for v in values]
            ),
        )
        return await self.patch_page(update)

    async def patch_date_property(
        self, property_name: str, date_value: str | dict
    ) -> PageDto:
        date = (
            DateValue(**date_value)
            if isinstance(date_value, dict)
            else DateValue(start=date_value)
        )
        update = self._build_update(property_name, PageDateProperty(date=date))
        return await self.patch_page(update)

    async def patch_status_property(self, property_name: str, status: str) -> PageDto:
        update = self._build_update(
            property_name, PageStatusProperty(status=StatusOption(id="", name=status))
        )
        return await self.patch_page(update)

    async def patch_relation_property(
        self, property_name: str, relation_ids: str | list[str]
    ) -> PageDto:
        ids = [relation_ids] if isinstance(relation_ids, str) else relation_ids
        update = self._build_update(
            property_name,
            PageRelationProperty(relation=[RelationItem(id=i) for i in ids]),
        )
        return await self.patch_page(update)
