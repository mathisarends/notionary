from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

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
            PropertyType.RICH_TEXT: lambda prop_name, prop_value: self.set_rich_text_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.URL: lambda prop_name, prop_value: self.set_url_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.EMAIL: lambda prop_name, prop_value: self.set_email_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.PHONE_NUMBER: lambda prop_name, prop_value: self.set_phone_number_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.NUMBER: lambda prop_name, prop_value: self.set_number_property(
                prop_name, self._validate_number(prop_value, prop_name)
            ),
            PropertyType.CHECKBOX: lambda prop_name, prop_value: self.set_checkbox_property(
                prop_name, self._validate_boolean(prop_value, prop_name)
            ),
            PropertyType.SELECT: lambda prop_name, prop_value: self.set_select_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.MULTI_SELECT: lambda prop_name, prop_value: self.set_multi_select_property(
                prop_name, self._validate_string_list(prop_value, prop_name)
            ),
            PropertyType.DATE: lambda prop_name, prop_value: self.set_date_property(
                prop_name, self._validate_date(prop_value, prop_name)
            ),
            PropertyType.STATUS: lambda prop_name, prop_value: self.set_status_property(
                prop_name, self._validate_string(prop_value, prop_name)
            ),
            PropertyType.RELATION: lambda prop_name, prop_value: self.set_relation_property_by_relation_values(
                prop_name, self._validate_relation(prop_value, prop_name)
            ),
        }

    def _validate_string(self, value: Any, property_name: str) -> str:
        """Validate that value is a string or can be safely converted to one."""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        raise TypeError(
            f"Property '{property_name}' expects string, got {type(value).__name__}: {value!r}"
        )

    def _validate_number(self, value: Any, property_name: str) -> float:
        """Validate that value is a number or can be converted to one."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError as e:
                raise ValueError(
                    f"Property '{property_name}' expects number, cannot convert string '{value}' to number"
                ) from e
        raise TypeError(
            f"Property '{property_name}' expects number, got {type(value).__name__}: {value!r}"
        )

    def _validate_boolean(self, value: Any, property_name: str) -> bool:
        if isinstance(value, bool):
            return value
        raise TypeError(
            f"Property '{property_name}' expects boolean, got {type(value).__name__}: {value!r}"
        )

    def _validate_string_list(self, value: Any, property_name: str) -> list[str]:
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            result = []
            for i, item in enumerate(value):
                try:
                    result.append(self._validate_string(item, f"{property_name}[{i}]"))
                except (TypeError, ValueError) as e:
                    raise TypeError(
                        f"Property '{property_name}' expects list of strings, "
                        f"but item at index {i} is invalid: {e}"
                    ) from e
            return result
        raise TypeError(
            f"Property '{property_name}' expects list of strings, got {type(value).__name__}: {value!r}"
        )

    def _validate_date(self, value: Any, property_name: str) -> str | dict:
        if isinstance(value, (str, dict)):
            return value
        raise TypeError(
            f"Property '{property_name}' expects string or dict for date, "
            f"got {type(value).__name__}: {value!r}"
        )

    def _validate_relation(self, value: Any, property_name: str) -> str | list[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            result = []
            for i, item in enumerate(value):
                if isinstance(item, str):
                    result.append(item)
                else:
                    raise TypeError(
                        f"Property '{property_name}' expects string or list of strings for relations, "
                        f"but item at index {i} is {type(item).__name__}: {item!r}"
                    )
            return result
        raise TypeError(
            f"Property '{property_name}' expects string or list of strings for relations, "
            f"got {type(value).__name__}: {value!r}"
        )

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
        self, property_name: str, number: int | float
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
        self, property_name: str, date_value: str | dict
    ) -> None:
        await self._notion_page._page_client.patch_date_property(
            property_name, date_value
        )

    async def set_status_property(self, property_name: str, status_name: str) -> None:
        await self._notion_page._page_client.patch_status_property(
            property_name, status_name
        )

    async def set_relation_property_by_relation_values(
        self, property_name: str, relation_values: str | list[str]
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
        self, relation_values: str | list[str]
    ) -> list[str]:
        return (
            relation_values if isinstance(relation_values, list) else [relation_values]
        )
