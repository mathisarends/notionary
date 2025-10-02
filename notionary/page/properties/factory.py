from notionary.page.page_models import NotionPageDto
from notionary.page.properties.client import PagePropertyHttpClient
from notionary.page.properties.service import PagePropertyHandler
from notionary.shared.entity.utils import extract_parent_data_source


class PagePropertyHandlerFactory:
    async def create_from_page_response(self, page_response: NotionPageDto) -> PagePropertyHandler:
        return PagePropertyHandler(
            properties=page_response.properties,
            parent_type=page_response.parent.type,
            page_url=page_response.url,
            parent_data_source=await extract_parent_data_source(page_response),
            page_property_http_client=self._create_http_client(page_id=page_response.id),
        )

    def _create_http_client(self, page_id: str) -> PagePropertyHttpClient:
        return PagePropertyHttpClient(page_id=page_id)
