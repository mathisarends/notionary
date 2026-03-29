from notionary.http.client import HttpClient
from notionary.page.page import Page
from notionary.page.properties import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.rich_text import rich_text_to_markdown


def to_page(dto: PageDto, http: HttpClient) -> Page:
    title_property = next(
        (p for p in dto.properties.values() if isinstance(p, PageTitleProperty)),
        None,
    )
    title = rich_text_to_markdown(title_property.title if title_property else [])
    return Page(
        id=dto.id,
        url=dto.url,
        title=title,
        icon=dto.icon,
        cover=dto.cover,
        in_trash=dto.in_trash,
        properties=dto.properties,
        http=http,
        created_time=dto.created_time,
        created_by=dto.created_by,
        last_edited_time=dto.last_edited_time,
        last_edited_by=dto.last_edited_by,
    )
