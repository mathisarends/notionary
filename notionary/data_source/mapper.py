from notionary.data_source.data_source import DataSource
from notionary.data_source.schemas import DataSourceDto
from notionary.http.client import HttpClient
from notionary.rich_text import rich_text_to_markdown


def to_data_source(dto: DataSourceDto, http: HttpClient) -> DataSource:
    title = rich_text_to_markdown(dto.title)
    description_text = rich_text_to_markdown(dto.description)
    return DataSource(
        id=dto.id,
        url=dto.url,
        title=title,
        description=description_text if description_text else None,
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
