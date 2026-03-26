from notionary.http.client import HttpClient
from notionary.page.comments.service import PageComments
from notionary.page.page import Page
from notionary.page.properties import (
    PagePropertyHandler,
    PagePropertyHttpClient,
    PageTitleProperty,
)
from notionary.page.schemas import PageDto
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class PageFactory:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def from_id(self, page_id: str) -> Page:
        response = await self._http.get(f"pages/{page_id}")
        dto = PageDto.model_validate(response)
        return await self.from_dto(dto)

    async def from_dto(self, dto: PageDto) -> Page:
        title = self._extract_page_title(dto)

        return Page(
            id=dto.id,
            url=dto.url,
            title=title,
            archived=dto.archived,
            icon=dto.icon,
            cover=dto.cover,
            in_trash=dto.in_trash,
            page_property_handler=PagePropertyHandler(
                properties=dto.properties,
                page_property_http_client=PagePropertyHttpClient(
                    page_id=dto.id, http=self._http
                ),
            ),
            comments=PageComments(page_id=dto.id, http=self._http),
            http=self._http,
        )

    @staticmethod
    def _extract_page_title(dto: PageDto) -> str:
        title_property = next(
            (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
            None,
        )
        converter = RichTextToMarkdownConverter()
        return converter.convert(title_property.title if title_property else [])
