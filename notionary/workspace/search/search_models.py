from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

from notionary.data_source.data_source_models import DataSourceDto
from notionary.page.page_models import NotionPageDto

T = TypeVar("T", bound=BaseModel)

PageOrDataSource = DataSourceDto | NotionPageDto


class SearchResponse(BaseModel, Generic[T]):
    results: list[T]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]


PageSearchResponse = SearchResponse[NotionPageDto]
DataSourceSearchResponse = SearchResponse[DataSourceDto]
