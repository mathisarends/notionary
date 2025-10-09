from typing import cast

from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import NotionPageDto
from notionary.shared.models.parent_models import DataSourceParent, ParentType


class PagePropertyHandlerFactory:
    def create_from_page_response(self, page_response: NotionPageDto) -> PagePropertyHandler:
        return PagePropertyHandler(
            properties=page_response.properties,
            parent_type=page_response.parent.type,
            page_url=page_response.url,
            page_property_http_client=self._create_http_client(page_id=page_response.id),
            parent_data_source=self._extract_parent_data_source_id(page_response),
        )

    def _create_http_client(self, page_id: str) -> PagePropertyHttpClient:
        return PagePropertyHttpClient(page_id=page_id)

    def _extract_parent_data_source_id(self, response: NotionPageDto) -> str | None:
        if response.parent.type != ParentType.DATA_SOURCE_ID:
            return None
        data_source_parent = cast(DataSourceParent, response.parent)
        return data_source_parent.data_source_id if data_source_parent else None
