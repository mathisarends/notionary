from typing import cast

from notionary.http.client import HttpClient
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import PageDto
from notionary.shared.models.parent import DataSourceParent, ParentType


class PagePropertyHandlerFactory:
    def create_from_page_response(
        self, page_response: PageDto, http: HttpClient
    ) -> PagePropertyHandler:
        return PagePropertyHandler(
            properties=page_response.properties,
            parent_type=page_response.parent.type,
            page_url=page_response.url,
            page_property_http_client=self._create_http_client(
                page_id=page_response.id, http=http
            ),
            parent_data_source=self._extract_parent_data_source_id(page_response),
        )

    def _create_http_client(
        self, page_id: str, http: HttpClient
    ) -> PagePropertyHttpClient:
        return PagePropertyHttpClient(page_id=page_id, http=http)

    def _extract_parent_data_source_id(self, response: PageDto) -> str | None:
        if response.parent.type != ParentType.DATA_SOURCE_ID:
            return None
        data_source_parent = cast(DataSourceParent, response.parent)
        return data_source_parent.data_source_id if data_source_parent else None
