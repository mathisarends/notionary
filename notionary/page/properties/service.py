from typing import Any
from uuid import UUID

from notionary.http import HttpClient
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.schemas import AnyPageProperty, PageTitleProperty


class PageProperties:
    """Scoped access to the properties of a single Notion page."""

    def __init__(
        self,
        id: UUID,
        properties: dict[str, AnyPageProperty],
        http: HttpClient,
    ) -> None:
        self.properties = properties
        self._property_http_client = PagePropertyHttpClient(
            page_id=id, http=http, properties=properties
        )

    async def set_property(self, name: str, value: Any) -> None:
        """Set a page property by name.

        Args:
            name: Property name as it appears in Notion.
            value: New value for the property.
        """
        dto = await self._property_http_client.set_property(name, value)
        self.properties = dto.properties

    async def set_title(self, title: str) -> None:
        """Set the page title.

        Args:
            title: New title text.

        Raises:
            KeyError: If the page has no title property.
        """
        name = next(
            (k for k, p in self.properties.items() if isinstance(p, PageTitleProperty)),
            None,
        )
        if name is None:
            raise KeyError("No title property found on this page.")
        await self.set_property(name, title)
