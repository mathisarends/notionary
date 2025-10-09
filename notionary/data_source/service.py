from __future__ import annotations

import asyncio
import difflib
from typing import TYPE_CHECKING, Any, Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.http.client import DataSourceClient
from notionary.data_source.http.data_source_instance_client import DataSourceInstanceClient
from notionary.data_source.properties.models import DataSourceProperty
from notionary.data_source.query.schema import FilterCondition
from notionary.data_source.schemas import DataSourceDto
from notionary.exceptions.data_source import DataSourcePropertyNotFound
from notionary.search.service import SearchService
from notionary.shared.entity.dto_parsers import (
    extract_cover_image_url_from_dto,
    extract_database_id,
    extract_description,
    extract_emoji_icon_from_dto,
    extract_external_icon_url_from_dto,
    extract_title,
)
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.entity.service import Entity
from notionary.shared.properties.property_type import PropertyType
from notionary.user.schemas import PartialUserDto

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionPage


class NotionDataSource(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        archived: bool,
        in_trash: bool,
        parent_database_id: str | None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        properties: dict[str, DataSourceProperty] | None = None,
        data_source_instance_client: DataSourceInstanceClient | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._parent_database_id = parent_database_id
        self._parent_database: NotionDatabase | None = None
        self._title = title
        self._archived = archived
        self._description = description
        self._properties = properties or {}
        self._data_source_client = data_source_instance_client or DataSourceInstanceClient(data_source_id=id)

    @classmethod
    async def from_id(
        cls,
        data_source_id: str,
        data_source_client: DataSourceClient | None = None,
        rich_text_converter: RichTextToMarkdownConverter | None = None,
    ) -> Self:
        client = data_source_client or DataSourceClient()
        converter = rich_text_converter or RichTextToMarkdownConverter()
        data_source_dto = await client.get_data_source(data_source_id)
        return await cls._create_from_dto(data_source_dto, converter)

    @classmethod
    async def from_title(
        cls,
        data_source_title: str,
        min_similarity: float = 0.6,
        search_service: SearchService | None = None,
    ) -> Self:
        service = search_service or SearchService()
        return await service.find_data_source(data_source_title, min_similarity=min_similarity)

    @classmethod
    async def _create_from_dto(
        cls,
        response: DataSourceDto,
        rich_text_converter: RichTextToMarkdownConverter,
    ) -> Self:
        title, description = await asyncio.gather(
            extract_title(response, rich_text_converter),
            extract_description(response, rich_text_converter),
        )

        parent_database_id = extract_database_id(response)

        return cls._create(
            id=response.id,
            title=title,
            description=description,
            created_time=response.created_time,
            created_by=response.created_by,
            last_edited_time=response.last_edited_time,
            last_edited_by=response.last_edited_by,
            archived=response.archived,
            in_trash=response.in_trash,
            properties=response.properties,
            parent_database_id=parent_database_id,
            emoji_icon=extract_emoji_icon_from_dto(response),
            external_icon_url=extract_external_icon_url_from_dto(response),
            cover_image_url=extract_cover_image_url_from_dto(response),
        )

    @classmethod
    def _create(
        cls,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        archived: bool,
        in_trash: bool,
        properties: dict[str, DataSourceProperty],
        parent_database_id: str | None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
    ) -> Self:
        data_source_instance_client = DataSourceInstanceClient(data_source_id=id)
        return cls(
            id=id,
            title=title,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            archived=archived,
            in_trash=in_trash,
            parent_database_id=parent_database_id,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
            description=description,
            properties=properties,
            data_source_instance_client=data_source_instance_client,
        )

    @property
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        return self._data_source_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def archived(self) -> bool:
        return self._archived

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def properties(self) -> dict[str, DataSourceProperty]:
        return self._properties

    async def get_parent_database(self) -> NotionDatabase | None:
        if self._parent_database is None and self._parent_database_id:
            self._parent_database = await NotionDatabase.from_id(self._parent_database_id)
        return self._parent_database

    async def create_blank_page(self, title: str | None = None) -> NotionPage:
        return await self._data_source_client.create_blank_page(title=title)

    async def set_title(self, title: str) -> None:
        data_source_dto = await self._data_source_client.update_title(title)
        self._title = data_source_dto.title

    async def archive(self) -> None:
        if self._archived:
            self.logger.info("Data source is already archived.")
            return
        await self._data_source_client.archive()
        self._archived = True

    async def unarchive(self) -> None:
        if not self._archived:
            self.logger.info("Data source is not archived.")
            return
        await self._data_source_client.unarchive()
        self._archived = False

    async def update_description(self, description: str) -> None:
        self._description = await self._data_source_client.update_description(description)

    async def get_pages(self, filters: list[FilterCondition] | None = None) -> list[NotionPage]:
        from notionary import NotionPage

        query_kwargs = {}
        if filters:
            filter_obj = self._build_notion_filter(filters)
            query_kwargs = {"filter": filter_obj}

        query_response = await self._data_source_client.query(filter=query_kwargs)
        return [await NotionPage.from_id(page.id) for page in query_response.results]

    def _build_notion_filter(self, filters: list[FilterCondition]) -> dict[str, Any]:
        if len(filters) == 1:
            return self._build_single_filter(filters[0])

        return {"and": [self._build_single_filter(f) for f in filters]}

    def _build_single_filter(self, filter_condition: FilterCondition) -> dict[str, Any]:
        prop = self._properties.get(filter_condition.field)
        if not prop:
            raise DataSourcePropertyNotFound(
                property_name=filter_condition.field,
                suggestions=self._find_closest_property_names(filter_condition.field),
            )

        property_type_key = self._get_notion_property_type_key_from_property(prop)
        notion_operator = self._map_operator_to_notion(filter_condition.operator)

        filter_dict: dict[str, Any] = {
            "property": filter_condition.field,
            property_type_key: {
                notion_operator: filter_condition.value if filter_condition.value is not None else True
            },
        }

        return filter_dict

    def _get_notion_property_type_key_from_property(self, prop: DataSourceProperty) -> str:
        type_key_mapping = {
            PropertyType.TITLE: "title",
            PropertyType.RICH_TEXT: "rich_text",
            PropertyType.SELECT: "select",
            PropertyType.MULTI_SELECT: "multi_select",
            PropertyType.STATUS: "status",
            PropertyType.NUMBER: "number",
            PropertyType.CHECKBOX: "checkbox",
            PropertyType.DATE: "date",
            PropertyType.CREATED_TIME: "created_time",
            PropertyType.LAST_EDITED_TIME: "last_edited_time",
            PropertyType.EMAIL: "email",
            PropertyType.PHONE_NUMBER: "phone_number",
            PropertyType.URL: "url",
            PropertyType.PEOPLE: "people",
            PropertyType.RELATION: "relation",
        }

        return type_key_mapping.get(prop.type, "rich_text")

    def _map_operator_to_notion(self, operator: str | Any) -> str:
        if hasattr(operator, "value"):
            operator_str = operator.value
        elif isinstance(operator, str):
            operator_str = operator
        else:
            operator_str = str(operator)

        operator_mapping = {
            "not_equals": "does_not_equal",
            "not_contains": "does_not_contain",
            "is_true": "equals",
            "is_false": "equals",
            "greater_than_or_equal": "on_or_after",
            "less_than_or_equal": "on_or_before",
        }

        return operator_mapping.get(operator_str, operator_str)

    def _find_closest_property_names(self, property_name: str, max_matches: int = 5) -> list[str]:
        if not self._properties:
            return []

        keys = list(self._properties.keys())
        matches = difflib.get_close_matches(property_name, keys, n=max_matches, cutoff=0.6)
        return matches
