from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from notionary.page.page_factory import load_page_from_title
from notionary.page.properties.page_property_http_client import PagePropertyHttpClient
from notionary.page.properties.page_property_models import (
    PropertyType,
)

if TYPE_CHECKING:
    from notionary import NotionPage


class PagePropertyWriter:
    def __init__(self, notion_page: NotionPage) -> None:
        self._notion_page = notion_page
        self._parent_data_source = notion_page._parent_data_source

        self._property_http_client = PagePropertyHttpClient(page_id=notion_page.id)

    async def set_title_property(self, title: str) -> None:
        updated_page = await self._property_http_client.patch_title(title)
        self._notion_page._properties = updated_page.properties
        self._notion_page._title = title

    async def set_rich_text_property(self, property_name: str, text: str) -> None:
        updated_page = await self._property_http_client.patch_rich_text_property(property_name, text)
        self._notion_page._properties = updated_page.properties

    async def set_url_property(self, property_name: str, url: str) -> None:
        updated_page = await self._property_http_client.patch_url_property(property_name, url)
        self._notion_page._properties = updated_page.properties

    async def set_email_property(self, property_name: str, email: str) -> None:
        updated_page = await self._property_http_client.patch_email_property(property_name, email)
        self._notion_page._properties = updated_page.properties

    async def set_phone_number_property(self, property_name: str, phone_number: str) -> None:
        updated_page = await self._property_http_client.patch_phone_property(property_name, phone_number)
        self._notion_page._properties = updated_page.properties

    async def set_number_property(self, property_name: str, number: int | float) -> None:
        updated_page = await self._property_http_client.patch_number_property(property_name, number)
        self._notion_page._properties = updated_page.properties

    async def set_checkbox_property(self, property_name: str, checked: bool) -> None:
        updated_page = await self._property_http_client.patch_checkbox_property(property_name, checked)
        self._notion_page._properties = updated_page.properties

    async def set_date_property(self, property_name: str, date_value: str | dict) -> None:
        updated_page = await self._property_http_client.patch_date_property(property_name, date_value)
        self._notion_page._properties = updated_page.properties

    async def set_select_property_by_option_name(self, property_name: str, option_name: str) -> None:
        updated_page = await self._property_http_client.patch_select_property(property_name, option_name)
        self._notion_page._properties = updated_page.properties

    async def set_multi_select_property_by_option_names(self, property_name: str, option_names: list[str]) -> None:
        updated_page = await self._property_http_client.patch_multi_select_property(property_name, option_names)
        self._notion_page._properties = updated_page.properties

    async def set_status_property_by_option_name(self, property_name: str, status: str) -> None:
        updated_page = await self._property_http_client.patch_status_property(property_name, status)
        self._notion_page._properties = updated_page.properties

    async def set_relation_property_by_page_titles(self, property_name: str, page_titles: list[str]) -> None:
        if not self._parent_data_source:
            return

        property_type = self._parent_data_source.property_reader.get_property_type_by_name(property_name)
        if property_type != PropertyType.RELATION:
            return

        relation_ids = await self._convert_page_titles_to_ids(page_titles)
        updated_page = await self._property_http_client.patch_relation_property(property_name, relation_ids)
        self._notion_page._properties = updated_page.properties

    async def _convert_page_titles_to_ids(self, page_titles: list[str]) -> list[str]:
        if not page_titles:
            return []

        pages = await asyncio.gather(
            *[
                load_page_from_title(
                    title=title,
                )
                for title in page_titles
            ]
        )

        return [page.id for page in pages]
