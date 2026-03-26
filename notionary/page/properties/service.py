from collections.abc import Coroutine
from typing import Any

from notionary.page.exceptions import (
    PagePropertyNotFoundError,
    PagePropertyTypeError,
)
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.schemas import (
    AnyPageProperty,
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePeopleProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
)
from notionary.page.schemas import PageDto
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class PagePropertyHandler:
    def __init__(
        self,
        properties: dict[str, AnyPageProperty],
        page_property_http_client: PagePropertyHttpClient,
    ) -> None:
        self._properties = properties
        self._property_http_client = page_property_http_client
        self._data_source_loaded = False
        self._rich_text_converter = RichTextToMarkdownConverter()

    def get_status(self, name: str) -> str | None:
        prop = self._get_typed_property_or_raise(name, PageStatusProperty)
        return prop.status.name if prop.status else None

    def get_select(self, name: str) -> str | None:
        prop = self._get_typed_property_or_raise(name, PageSelectProperty)
        return prop.select.name if prop.select else None

    def get_title(self, name: str) -> str:
        prop = self._get_typed_property_or_raise(name, PageTitleProperty)
        return self._rich_text_converter.convert(prop.title)

    def get_people(self, property_name: str) -> list[str]:
        prop = self._get_typed_property_or_raise(property_name, PagePeopleProperty)
        return [person.name for person in prop.people if person.name]

    def get_created_time(self, name: str) -> str | None:
        return self._get_typed_property_or_raise(
            name, PageCreatedTimeProperty
        ).created_time

    def get_relation_ids(self, name: str) -> list[str]:
        prop = self._get_typed_property_or_raise(name, PageRelationProperty)
        return [rel.id for rel in prop.relation]

    def get_multiselect(self, name: str) -> list[str]:
        prop = self._get_typed_property_or_raise(name, PageMultiSelectProperty)
        return [option.name for option in prop.multi_select]

    def get_url(self, name: str) -> str | None:
        return self._get_typed_property_or_raise(name, PageURLProperty).url

    def get_number(self, name: str) -> float | None:
        return self._get_typed_property_or_raise(name, PageNumberProperty).number

    def get_checkbox(self, name: str) -> bool:
        return self._get_typed_property_or_raise(name, PageCheckboxProperty).checkbox

    def get_date(self, name: str) -> str | None:
        prop = self._get_typed_property_or_raise(name, PageDateProperty)
        return prop.date.start if prop.date else None

    def get_rich_text(self, name: str) -> str:
        prop = self._get_typed_property_or_raise(name, PageRichTextProperty)
        return self._rich_text_converter.convert(prop.rich_text)

    def get_email(self, name: str) -> str | None:
        return self._get_typed_property_or_raise(name, PageEmailProperty).email

    def get_phone(self, name: str) -> str | None:
        return self._get_typed_property_or_raise(
            name, PagePhoneNumberProperty
        ).phone_number

    async def set_title(self, title: str) -> None:
        title_property_name = self._extract_title_property_name()
        await self._apply_patch(
            title_property_name,
            PageTitleProperty,
            self._property_http_client.patch_title(title_property_name, title),
        )

    async def set_rich_text(self, property_name: str, text: str) -> None:
        await self._apply_patch(
            property_name,
            PageRichTextProperty,
            self._property_http_client.patch_rich_text_property(property_name, text),
        )

    async def set_url(self, property_name: str, url: str) -> None:
        await self._apply_patch(
            property_name,
            PageURLProperty,
            self._property_http_client.patch_url_property(property_name, url),
        )

    async def set_email(self, property_name: str, email: str) -> None:
        await self._apply_patch(
            property_name,
            PageEmailProperty,
            self._property_http_client.patch_email_property(property_name, email),
        )

    async def set_phone(self, property_name: str, phone_number: str) -> None:
        await self._apply_patch(
            property_name,
            PagePhoneNumberProperty,
            self._property_http_client.patch_phone_property(
                property_name, phone_number
            ),
        )

    async def set_number(self, property_name: str, number: int | float) -> None:
        await self._apply_patch(
            property_name,
            PageNumberProperty,
            self._property_http_client.patch_number_property(property_name, number),
        )

    async def set_checkbox(self, property_name: str, checked: bool) -> None:
        await self._apply_patch(
            property_name,
            PageCheckboxProperty,
            self._property_http_client.patch_checkbox_property(property_name, checked),
        )

    async def set_date(self, property_name: str, date_value: str | dict) -> None:
        await self._apply_patch(
            property_name,
            PageDateProperty,
            self._property_http_client.patch_date_property(property_name, date_value),
        )

    async def set_select(self, property_name: str, option_name: str) -> None:
        await self._apply_patch(
            property_name,
            PageSelectProperty,
            self._property_http_client.patch_select_property(
                property_name, option_name
            ),
        )

    async def set_multiselect(
        self, property_name: str, option_names: list[str]
    ) -> None:
        await self._apply_patch(
            property_name,
            PageMultiSelectProperty,
            self._property_http_client.patch_multi_select_property(
                property_name, option_names
            ),
        )

    async def set_status(self, property_name: str, status: str) -> None:
        await self._apply_patch(
            property_name,
            PageStatusProperty,
            self._property_http_client.patch_status_property(property_name, status),
        )

    async def set_relation(self, property_name: str, page_ids: list[str]) -> None:
        await self._apply_patch(
            property_name,
            PageRelationProperty,
            self._property_http_client.patch_relation_property(property_name, page_ids),
        )

    async def _apply_patch[T: PageProperty](
        self,
        name: str,
        expected_type: type[T],
        coro: Coroutine[Any, Any, PageDto],
    ) -> None:
        self._get_typed_property_or_raise(name, expected_type)
        self._properties = (await coro).properties

    def _get_typed_property_or_raise[T: PageProperty](
        self, name: str, property_type: type[T]
    ) -> T:
        prop = self._properties.get(name)

        if prop is None:
            raise PagePropertyNotFoundError(
                property_name=name,
                available_properties=list(self._properties.keys()),
            )
        if not isinstance(prop, property_type):
            raise PagePropertyTypeError(
                property_name=name,
                actual_type=type(prop).__name__,
            )

        return prop

    def _extract_title_property_name(self) -> str | None:
        return next(
            (
                key
                for key, prop in self._properties.items()
                if isinstance(prop, PageTitleProperty)
            ),
            None,
        )
