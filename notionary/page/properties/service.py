from typing import Any

from notionary.http import HttpClient
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.schemas import AnyPageProperty, PageTitleProperty


class PagePropertyHandler:
    def __init__(
        self,
        properties: dict[str, AnyPageProperty],
        id: str,
        http: HttpClient,
    ) -> None:
        self.properties = properties
        self._property_http_client = PagePropertyHttpClient(
            page_id=id, http=http, properties=properties
        )

    async def set_property(self, name: str, value: Any) -> None:
        dto = await self._property_http_client.set_property(name, value)
        self.properties = dto.properties

    async def set_title(self, title: str) -> None:
        name = next(
            (k for k, p in self.properties.items() if isinstance(p, PageTitleProperty)),
            None,
        )
        if name is None:
            raise KeyError("No title property found on this page.")
        await self.set_property(name, title)
