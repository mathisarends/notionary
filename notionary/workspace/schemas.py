from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

from notionary.data_source.schemas import DataSourceDto
from notionary.page.schemas import PageDto

T = TypeVar("T", bound=BaseModel)

PageOrDataSource = DataSourceDto | PageDto


class SearchResponse(BaseModel, Generic[T]):
    results: list[T]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]


PageSearchResponse = SearchResponse[PageDto]
DataSourceSearchResponse = SearchResponse[DataSourceDto]
