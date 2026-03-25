import logging
from collections.abc import AsyncIterator

from notionary.data_source.data_source_instance_client import (
    DataSourceInstanceClient,
)
from notionary.data_source.exceptions import (
    DataSourcePropertyNotFound,
    DataSourcePropertyTypeError,
)
from notionary.data_source.properties.schemas import (
    DataSourceMultiSelectProperty,
    DataSourceProperty,
    DataSourcePropertyOption,
    DataSourcePropertyT,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.query import (
    DataSourceQueryBuilder,
    DataSourceQueryParams,
    QueryResolver,
)
from notionary.data_source.schemas import DataSourceDto
from notionary.database import Database
from notionary.page import Page
from notionary.page.properties.schemas import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.shared.entity.cover import EntityCover
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.metadata import EntityMetadata
from notionary.shared.entity.trash import EntityTrash
from notionary.shared.icon.icon import EntityIcon

logger = logging.getLogger(__name__)


class DataSource:
    def __init__(
        self,
        dto: DataSourceDto,
        title: str,
        description: str | None,
        properties: dict[str, DataSourceProperty],
        data_source_instance_client: DataSourceInstanceClient,
        entity_update_client: EntityMetadataUpdateClient,
        query_resolver: QueryResolver | None = None,
    ) -> None:
        self.metadata = EntityMetadata.from_dto(dto)

        self._icon = EntityIcon(dto, entity_update_client)
        self._cover = EntityCover(dto, entity_update_client)
        self._trash = EntityTrash(dto, entity_update_client)

        self._parent_database: Database | None = None
        self._title = title
        self._archived = dto.archived
        self._description = description
        self._properties = properties or {}
        self._data_source_client = data_source_instance_client
        self.query_resolver = query_resolver or QueryResolver()

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def url(self) -> str:
        return self.metadata.url

    @property
    def in_trash(self) -> bool:
        return self._trash.in_trash

    async def trash(self) -> None:
        await self._trash.trash()

    async def restore(self) -> None:
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        await self._icon.set_from_url(url)

    async def remove_icon(self) -> None:
        await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        await self._cover.set_random_gradient()

    async def remove_cover(self) -> None:
        await self._cover.remove()

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

    @property
    def data_source_query_builder(self) -> DataSourceQueryBuilder:
        return DataSourceQueryBuilder(properties=self._properties)

    async def set_title(self, title: str) -> None:
        data_source_dto = await self._data_source_client.update_title(title)
        self._title = data_source_dto.title

    async def archive(self) -> None:
        if self._archived:
            logger.info("Data source is already archived.")
            return
        await self._data_source_client.archive()
        self._archived = True

    async def unarchive(self) -> None:
        if not self._archived:
            logger.info("Data source is not archived.")
            return
        await self._data_source_client.unarchive()
        self._archived = False

    async def update_description(self, description: str) -> None:
        self._description = await self._data_source_client.update_description(
            description
        )

    async def create_blank_page(self, title: str | None = None) -> Page:
        return await self._data_source_client.create_blank_page(title=title)

    async def get_pages(
        self,
        query_params: DataSourceQueryParams | None = None,
    ) -> list[Page]:
        from notionary import Page

        resolved_params = await self._resolve_query_params_if_needed(query_params)
        query_response = await self._data_source_client.query(
            query_params=resolved_params
        )
        return [await Page.from_id(page.id) for page in query_response.results]

    async def iter_pages(
        self,
        query_params: DataSourceQueryParams | None = None,
    ) -> AsyncIterator[Page]:
        from notionary import Page

        resolved_params = await self._resolve_query_params_if_needed(query_params)

        async for page in self._data_source_client.query_stream(
            query_params=resolved_params
        ):
            yield await Page.from_id(page.id)

    async def _resolve_query_params_if_needed(
        self,
        query_params: DataSourceQueryParams | None,
    ) -> DataSourceQueryParams | None:
        if query_params is None:
            return None
        return await self.query_resolver.resolve_params(query_params)

    # ── Properties ───────────────────────────────────────────────
    def get_query_builder(self) -> DataSourceQueryBuilder:
        return DataSourceQueryBuilder(properties=self._properties)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        prop = self._properties.get(property_name)

        if prop is None:
            return []

        if isinstance(prop, DataSourceSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceMultiSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceStatusProperty):
            return prop.option_names

        if isinstance(prop, DataSourceRelationProperty):
            return await self._get_relation_options(prop)

        return []

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        select_prop = self._get_typed_property_or_raise(
            property_name, DataSourceSelectProperty
        )
        return select_prop.option_names

    def get_multi_select_options_by_property_name(
        self, property_name: str
    ) -> list[DataSourcePropertyOption]:
        multi_select_prop = self._get_typed_property_or_raise(
            property_name, DataSourceMultiSelectProperty
        )
        return multi_select_prop.option_names

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        status_prop = self._get_typed_property_or_raise(
            property_name, DataSourceStatusProperty
        )
        return status_prop.option_names

    async def get_relation_options_by_property_name(
        self, property_name: str
    ) -> list[str]:
        relation_prop = self._get_typed_property_or_raise(
            property_name, DataSourceRelationProperty
        )
        return await self._get_relation_options(relation_prop)

    async def _get_relation_options(
        self, relation_prop: DataSourceRelationProperty
    ) -> list[str]:
        related_data_source_id = relation_prop.related_data_source_id
        if not related_data_source_id:
            return []

        async with DataSourceInstanceClient(related_data_source_id) as related_client:
            search_results = await related_client.query()

        page_titles = []
        for page_response in search_results.results:
            title = self._extract_title_from_notion_page_dto(page_response)
            if title:
                page_titles.append(title)

        return page_titles

    def _extract_title_from_notion_page_dto(self, page: PageDto) -> str | None:
        if not page.properties:
            return None

        title_property = next(
            (
                prop
                for prop in page.properties.values()
                if isinstance(prop, PageTitleProperty)
            ),
            None,
        )

        if not title_property:
            return None

        return "".join(item.plain_text for item in title_property.title)

    def _get_typed_property_or_raise(
        self, name: str, property_type: type[DataSourcePropertyT]
    ) -> DataSourcePropertyT:
        prop = self._properties.get(name)

        if prop is None:
            raise DataSourcePropertyNotFound(
                property_name=name,
                available_properties=list(self._properties.keys()),
            )

        if not isinstance(prop, property_type):
            raise DataSourcePropertyTypeError(
                property_name=name,
                expected_type=property_type.__name__,
                actual_type=type(prop).__name__,
            )

        return prop
