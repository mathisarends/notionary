from notionary.database.database import Database
from notionary.database.schemas import DatabaseDto
from notionary.http.client import HttpClient
from notionary.rich_text import rich_text_to_markdown


def to_database(dto: DatabaseDto, http: HttpClient) -> Database:
    title = rich_text_to_markdown(dto.title)
    description_text = rich_text_to_markdown(dto.description)
    return Database(
        id=dto.id,
        url=dto.url,
        title=title,
        description=description_text if description_text else None,
        is_inline=dto.is_inline,
        is_locked=dto.is_locked,
        data_sources=dto.data_sources,
        icon=dto.icon,
        cover=dto.cover,
        in_trash=dto.in_trash,
        http=http,
        created_time=dto.created_time,
        created_by=dto.created_by,
        last_edited_time=dto.last_edited_time,
        last_edited_by=dto.last_edited_by,
    )
