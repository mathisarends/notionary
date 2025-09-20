from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union

from notionary.page.page_factory import load_page_from_name
from notionary.page.properties.page_property_models import PropertyType

if TYPE_CHECKING:
    from notionary import NotionPage


Setter = Callable[[str, Any], Awaitable[None]]


class PagePropertyWriter:
    def __init__(self, notion_page: NotionPage):
        self._notion_page = notion_page
        self._property_setters = self._build_property_setters()

    def _build_property_setters(self) -> dict[PropertyType, Setter]:
        return {
            PropertyType.TITLE: lambda _prop_name, prop_value: self.set_title_property(
                str(prop_value)
            ),
            PropertyType.RICH_TEXT: lambda prop_name, prop_value: self.set_rich_text_property(
                prop_name, str(prop_value)
            ),
            PropertyType.URL: lambda prop_name, prop_value: self.set_url_property(
                prop_name, str(prop_value)
            ),
            PropertyType.EMAIL: lambda prop_name, prop_value: self.set_email_property(
                prop_name, str(prop_value)
            ),
            PropertyType.PHONE_NUMBER: lambda prop_name, prop_value: self.set_phone_number_property(
                prop_name, str(prop_value)
            ),
            PropertyType.NUMBER: lambda prop_name, prop_value: self.set_number_property(
                prop_name, float(prop_value)
            ),
            PropertyType.CHECKBOX: lambda prop_name, prop_value: self.set_checkbox_property(
                prop_name, bool(prop_value)
            ),
            PropertyType.SELECT: lambda prop_name, prop_value: self.set_select_property(
                prop_name, str(prop_value)
            ),
            PropertyType.MULTI_SELECT: lambda prop_name, prop_value: self.set_multi_select_property(
                prop_name,
                list(prop_value) if not isinstance(prop_value, str) else [prop_value],
            ),
            PropertyType.DATE: lambda prop_name, prop_value: self.set_date_property(
                prop_name, prop_value
            ),
            PropertyType.STATUS: lambda prop_name, prop_value: self.set_status_property(
                prop_name, str(prop_value)
            ),
            PropertyType.RELATION: lambda prop_name, prop_value: self.set_relation_property_by_relation_values(
                prop_name, prop_value
            ),
        }

    async def set_property_value_by_name(self, property_name: str, value: Any) -> Any:
        prop = self._notion_page.properties.get(property_name)
        if not prop:
            return None

        setter = self._property_setters.get(prop.type)
        if not setter:
            return None

        return await setter(property_name, value)

    async def set_title_property(self, title: str) -> None:
        await self._notion_page._page_client.patch_title(title)
        self._notion_page._title = title

    async def set_rich_text_property(self, property_name: str, text: str) -> None:
        await self._notion_page._page_client.patch_rich_text_property(
            property_name, text
        )

    async def set_url_property(self, property_name: str, url: str) -> None:
        await self._notion_page._page_client.patch_url_property(property_name, url)

    async def set_email_property(self, property_name: str, email: str) -> None:
        await self._notion_page._page_client.patch_email_property(property_name, email)

    async def set_phone_number_property(self, property_name: str, phone: str) -> None:
        await self._notion_page._page_client.patch_phone_property(property_name, phone)

    async def set_number_property(
        self, property_name: str, number: Union[int, float]
    ) -> None:
        await self._notion_page._page_client.patch_number_property(
            property_name, number
        )

    async def set_checkbox_property(self, property_name: str, checked: bool) -> None:
        await self._notion_page._page_client.patch_checkbox_property(
            property_name, checked
        )

    async def set_select_property(self, property_name: str, option_name: str) -> None:
        await self._notion_page._page_client.patch_select_property(
            property_name, option_name
        )

    async def set_multi_select_property(
        self, property_name: str, option_names: list[str]
    ) -> None:
        await self._notion_page._page_client.patch_multi_select_property(
            property_name, option_names
        )

    async def set_date_property(
        self, property_name: str, date_value: Union[str, dict]
    ) -> None:
        await self._notion_page._page_client.patch_date_property(
            property_name, date_value
        )

    async def set_status_property(self, property_name: str, status_name: str) -> None:
        await self._notion_page._page_client.patch_status_property(
            property_name, status_name
        )

    async def set_relation_property_by_relation_values(
        self, property_name: str, relation_values: Union[str, list[str]]
    ) -> None:
        relation_values = self._normalize_relation_values_to_list(relation_values)

        relation_ids = await self._convert_relation_values_to_page_ids(relation_values)

        await self._notion_page._page_client.patch_relation_property(
            property_name, relation_ids
        )

    async def _convert_relation_values_to_page_ids(
        self, relation_values: list[str]
    ) -> list[str]:
        if not relation_values:
            return []

        pages = await asyncio.gather(
            *[
                load_page_from_name(
                    page_name=title,
                    token=self._notion_page.token,
                )
                for title in relation_values
            ]
        )

        return [page.id for page in pages]

    def _normalize_relation_values_to_list(
        self, relation_values: Union[str, list[str]]
    ) -> list[str]:
        return (
            relation_values if isinstance(relation_values, list) else [relation_values]
        )
