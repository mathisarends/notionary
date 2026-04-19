from collections.abc import AsyncGenerator
from uuid import UUID

from notionary.data_source.query.filters import QueryFilter
from notionary.data_source.query.sorts import QuerySort
from notionary.data_source.schemas import (
    DataSourceDto,
    DataSourceTemplate,
    ListTemplatesResponse,
    QueryDataSourceRequest,
    QueryResultType,
    UpdateDataSourceDto,
)
from notionary.http.client import HttpClient
from notionary.page import Page
from notionary.page import mapper as page_mapper
from notionary.page.schemas import PageDto
from notionary.rich_text import markdown_to_rich_text


class DataSourceClient:
    def __init__(self, http: HttpClient, data_source_id: UUID) -> None:
        self._http = http
        self._data_source_id = data_source_id

    async def patch_metadata(
        self, update_data_source_dto: UpdateDataSourceDto
    ) -> DataSourceDto:
        response = await self._http.patch(
            f"data_sources/{self._data_source_id}", data=update_data_source_dto
        )
        return DataSourceDto.model_validate(response)

    async def set_title(self, title: str) -> DataSourceDto:
        rich_text_title = markdown_to_rich_text(title)
        update_data_source_dto = UpdateDataSourceDto(title=rich_text_title)
        return await self.patch_metadata(update_data_source_dto)

    async def create_page(
        self,
        title: str | None = None,
        *,
        template_id: str | None = None,
        use_default_template: bool = False,
    ) -> Page:
        if template_id is not None:
            template = {"type": "template_id", "template_id": template_id}
        elif use_default_template:
            template = {"type": "default"}
        else:
            template = None

        data = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": str(self._data_source_id),
            },
            "properties": {},
        }

        if title:
            data["properties"]["Name"] = {"title": [{"text": {"content": title}}]}

        if template:
            data["template"] = template

        response = await self._http.post("pages", data=data)
        dto = PageDto.model_validate(response)
        return page_mapper.to_page(dto, self._http)

    async def list_templates(
        self,
        name: str | None = None,
        page_size: int = 100,
    ) -> list[DataSourceTemplate]:
        templates: list[DataSourceTemplate] = []
        start_cursor: str | None = None

        while True:
            params: dict = {"page_size": page_size}
            if name is not None:
                params["name"] = name
            if start_cursor is not None:
                params["start_cursor"] = start_cursor

            response = await self._http.get(
                f"data_sources/{self._data_source_id}/templates",
                params=params,
            )
            page = ListTemplatesResponse.model_validate(response)
            templates.extend(page.templates)

            if not page.has_more or page.next_cursor is None:
                break
            start_cursor = page.next_cursor

        return templates

    async def query(
        self,
        *,
        filter: QueryFilter | None = None,
        sorts: list[QuerySort] | None = None,
        page_size: int | None = None,
        filter_properties: list[str] | None = None,
        in_trash: bool | None = None,
        limit: int | None = None,
    ) -> list[Page]:
        request = QueryDataSourceRequest(
            filter=filter,
            sorts=sorts,
            page_size=page_size,
            filter_properties=filter_properties,
            in_trash=in_trash,
            result_type=QueryResultType.PAGE,
        )
        payload = request.to_api_payload()
        endpoint = f"data_sources/{self._data_source_id}/query"

        raw_results = await self._http.paginate(
            endpoint, total_results_limit=limit, **payload
        )
        return [
            page_mapper.to_page(PageDto.model_validate(r), self._http)
            for r in raw_results
        ]

    async def iter_query(
        self,
        *,
        filter: QueryFilter | None = None,
        sorts: list[QuerySort] | None = None,
        page_size: int | None = None,
        filter_properties: list[str] | None = None,
        in_trash: bool | None = None,
        limit: int | None = None,
    ) -> AsyncGenerator[Page]:
        request = QueryDataSourceRequest(
            filter=filter,
            sorts=sorts,
            page_size=page_size,
            filter_properties=filter_properties,
            in_trash=in_trash,
            result_type=QueryResultType.PAGE,
        )
        payload = request.to_api_payload()
        endpoint = f"data_sources/{self._data_source_id}/query"

        async for raw in self._http.paginate_stream(
            endpoint, total_results_limit=limit, **payload
        ):
            yield page_mapper.to_page(PageDto.model_validate(raw), self._http)
