from notionary.http.client import HttpClient
from notionary.page.blocks.client import BlockClient
from notionary.page.blocks.content.factory import create_block_content_service
from notionary.page.comments.service import PageComments
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.factory import PagePropertyHandlerFactory
from notionary.page.properties.schemas import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.page.service import Page
from notionary.shared.rich_text.rich_text_to_markdown.factory import (
    create_rich_text_to_markdown_converter,
)


class PageFactory:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def from_id(self, page_id: str) -> Page:
        dto = await self._fetch_dto(page_id)
        return await self.from_dto(dto)

    async def from_dto(self, dto: PageDto) -> Page:
        title = await _extract_page_title(dto)
        block_client = BlockClient(self._http)

        return Page(
            dto=dto,
            title=title,
            page_property_handler=PagePropertyHandlerFactory().create_from_page_response(
                dto
            ),
            block_client=block_client,
            page_content=create_block_content_service(dto.id, block_client),
            page_comments=PageComments(page_id=dto.id, http=self._http),
            metadata_update_client=PageMetadataUpdateClient(dto.id, self._http),
        )

    async def _fetch_dto(self, page_id: str) -> PageDto:
        response = await self._http.get(f"pages/{page_id}")
        return PageDto.model_validate(response)


async def _extract_page_title(dto: PageDto) -> str:
    title_property = next(
        (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
        None,
    )
    converter = create_rich_text_to_markdown_converter()
    return await converter.convert(title_property.title if title_property else [])
