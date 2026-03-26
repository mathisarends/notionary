from typing import Any

from pydantic import BaseModel

from notionary.http.client import HttpClient
from notionary.page.properties.schemas import (
    AnyPageProperty,
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
    def __init__(
        self,
        page_id: str,
        http: HttpClient,
        properties: dict[str, AnyPageProperty],
    ) -> None:
        self._page_id = page_id
        self._http = http
        self._properties = properties

    async def patch_page(self, data: BaseModel) -> PageDto:
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        result_dict = await self._http.patch(f"pages/{self._page_id}", data=data_dict)
        return PageDto.model_validate(result_dict)

    async def set_property(self, name: str, value: Any) -> PageDto:
        prop = self._properties.get(name)
        if prop is None:
            raise KeyError(
                f"Property '{name}' not found. Available: {list(self._properties)}"
            )

        built = self._build_property(prop, value)
        return await self.patch_page(PgePropertiesUpdateDto(properties={name: built}))

    def _build_property(self, prop: AnyPageProperty, value: Any) -> PageProperty:
        match prop:
            case PageTitleProperty():
                return PageTitleProperty(
                    title=[RichText(type="text", text={"content": value})]
                )
            case PageRichTextProperty():
                return PageRichTextProperty(
                    rich_text=[RichText(type="text", text={"content": value})]
                )
            case PageURLProperty():
                return PageURLProperty(url=value)
            case PageEmailProperty():
                return PageEmailProperty(email=value)
            case PagePhoneNumberProperty():
                return PagePhoneNumberProperty(phone_number=value)
            case PageNumberProperty():
                return PageNumberProperty(number=value)
            case PageCheckboxProperty():
                return PageCheckboxProperty(checkbox=value)
            case PageSelectProperty():
                return PageSelectProperty(select=SelectOption(name=value))
            case PageMultiSelectProperty():
                return PageMultiSelectProperty(
                    multi_select=[SelectOption(name=v) for v in value]
                )
            case PageDateProperty():
                date = (
                    DateValue(**value)
                    if isinstance(value, dict)
                    else DateValue(start=value)
                )
                return PageDateProperty(date=date)
            case PageStatusProperty():
                return PageStatusProperty(status=StatusOption(id="", name=value))
            case PageRelationProperty():
                ids = [value] if isinstance(value, str) else value
                return PageRelationProperty(relation=[RelationItem(id=i) for i in ids])
            case _:
                raise TypeError(f"Unsupported property type: {type(prop).__name__}")
