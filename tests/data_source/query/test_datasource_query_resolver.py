from typing import cast
from unittest.mock import AsyncMock

import pytest

from notionary.blocks.rich_text.name_id_resolver.page import PageNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.person import PersonNameIdResolver
from notionary.data_source.query.resolver import QueryResolver
from notionary.data_source.query.schema import (
    CompoundFilter,
    DataSourceQueryParams,
    LogicalOperator,
    NumberOperator,
    PropertyFilter,
    StringOperator,
)
from notionary.shared.properties.property_type import PropertyType


@pytest.fixture
def mock_user_resolver() -> PersonNameIdResolver:
    mock_obj = AsyncMock(spec=PersonNameIdResolver)
    resolver = cast(PersonNameIdResolver, mock_obj)
    resolver.resolve_name_to_id = AsyncMock(return_value="user-uuid-123")
    return resolver


@pytest.fixture
def mock_page_resolver() -> PageNameIdResolver:
    mock_obj = AsyncMock(spec=PageNameIdResolver)
    resolver = cast(PageNameIdResolver, mock_obj)
    resolver.resolve_name_to_id = AsyncMock(return_value="page-uuid-456")
    return resolver


@pytest.fixture
def query_resolver(
    mock_user_resolver: PersonNameIdResolver,
    mock_page_resolver: PageNameIdResolver,
) -> QueryResolver:
    return QueryResolver(
        user_resolver=mock_user_resolver,
        page_resolver=mock_page_resolver,
    )


@pytest.fixture
def valid_uuid() -> str:
    return "6c574cee-ca68-41c8-86e0-1b9e992689fb"


@pytest.fixture
def valid_uuid_without_dashes() -> str:
    return "6c574ceeca6841c886e01b9e992689fb"


def _create_property_filter(
    property_name: str,
    property_type: PropertyType,
    operator: StringOperator | NumberOperator,
    value: str | int | None,
) -> PropertyFilter:
    return PropertyFilter(
        property=property_name,
        property_type=property_type,
        operator=operator,
        value=value,
    )


def _create_query_params(filter: PropertyFilter | CompoundFilter | None) -> DataSourceQueryParams:
    return DataSourceQueryParams(filter=filter, sorts=None)


class TestQueryResolverWithoutFilter:
    """Tests for QueryResolver with no filter."""

    @pytest.mark.asyncio
    async def test_should_return_params_unchanged_when_no_filter(
        self,
        query_resolver: QueryResolver,
    ) -> None:
        params = DataSourceQueryParams(filter=None, sorts=None)

        result = await query_resolver.resolve_params(params)

        assert result == params
        assert result.filter is None


class TestUuidDetection:
    @pytest.mark.parametrize(
        "uuid_value",
        [
            "6c574cee-ca68-41c8-86e0-1b9e992689fb",
            "6c574ceeca6841c886e01b9e992689fb",
            "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
            "a1b2c3d4e5f678901234567890abcdef",
        ],
    )
    def test_should_recognize_valid_uuid_formats(
        self,
        query_resolver: QueryResolver,
        uuid_value: str,
    ) -> None:
        result = query_resolver._is_uuid(uuid_value)

        assert result is True

    @pytest.mark.parametrize(
        "non_uuid_value",
        [
            "John Doe",
            "not-a-uuid",
            "12345",
            "",
            "6c574cee-ca68-41c8",
            123,
            None,
        ],
    )
    def test_should_not_recognize_invalid_uuid_formats(
        self,
        query_resolver: QueryResolver,
        non_uuid_value: str | int | None,
    ) -> None:
        result = query_resolver._is_uuid(non_uuid_value)

        assert result is False


class TestPeoplePropertyResolution:
    @pytest.mark.asyncio
    async def test_should_resolve_user_name_to_id_for_people_property(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
    ) -> None:
        filter = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value="John Doe",
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_user_resolver.resolve_name_to_id.assert_called_once_with("John Doe")
        assert result.filter.value == "user-uuid-123"

    @pytest.mark.asyncio
    async def test_should_not_resolve_when_value_is_already_uuid(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
        valid_uuid: str,
    ) -> None:
        filter = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value=valid_uuid,
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_user_resolver.resolve_name_to_id.assert_not_called()
        assert result.filter.value == valid_uuid

    @pytest.mark.asyncio
    async def test_should_raise_error_when_user_name_cannot_be_resolved(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
    ) -> None:
        mock_user_resolver.resolve_name_to_id = AsyncMock(return_value=None)

        filter = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value="Unknown User",
        )
        params = _create_query_params(filter)

        with pytest.raises(ValueError, match="Could not resolve user name 'Unknown User' to ID"):
            await query_resolver.resolve_params(params)


class TestRelationPropertyResolution:
    @pytest.mark.asyncio
    async def test_should_resolve_page_name_to_id_for_relation_property(
        self,
        query_resolver: QueryResolver,
        mock_page_resolver: PageNameIdResolver,
    ) -> None:
        filter = _create_property_filter(
            property_name="Related Tasks",
            property_type=PropertyType.RELATION,
            operator=StringOperator.CONTAINS,
            value="Task Title",
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_page_resolver.resolve_name_to_id.assert_called_once_with("Task Title")
        assert result.filter.value == "page-uuid-456"

    @pytest.mark.asyncio
    async def test_should_not_resolve_when_value_is_uuid_without_dashes(
        self,
        query_resolver: QueryResolver,
        mock_page_resolver: PageNameIdResolver,
        valid_uuid_without_dashes: str,
    ) -> None:
        filter = _create_property_filter(
            property_name="Related Tasks",
            property_type=PropertyType.RELATION,
            operator=StringOperator.CONTAINS,
            value=valid_uuid_without_dashes,
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_page_resolver.resolve_name_to_id.assert_not_called()
        assert result.filter.value == valid_uuid_without_dashes

    @pytest.mark.asyncio
    async def test_should_raise_error_when_page_name_cannot_be_resolved(
        self,
        query_resolver: QueryResolver,
        mock_page_resolver: PageNameIdResolver,
    ) -> None:
        mock_page_resolver.resolve_name_to_id = AsyncMock(return_value=None)

        filter = _create_property_filter(
            property_name="Related Tasks",
            property_type=PropertyType.RELATION,
            operator=StringOperator.CONTAINS,
            value="Unknown Page",
        )
        params = _create_query_params(filter)

        with pytest.raises(ValueError, match="Could not resolve page name 'Unknown Page' to ID"):
            await query_resolver.resolve_params(params)


class TestNonResolvableProperties:
    """Tests for properties that should not be resolved."""

    @pytest.mark.asyncio
    async def test_should_not_resolve_string_property(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
    ) -> None:
        filter = _create_property_filter(
            property_name="Status",
            property_type=PropertyType.STATUS,
            operator=StringOperator.EQUALS,
            value="Active",
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_user_resolver.resolve_name_to_id.assert_not_called()
        assert result.filter.value == "Active"

    @pytest.mark.asyncio
    async def test_should_not_resolve_number_property(
        self,
        query_resolver: QueryResolver,
    ) -> None:
        filter = _create_property_filter(
            property_name="Count",
            property_type=PropertyType.NUMBER,
            operator=NumberOperator.GREATER_THAN,
            value=5,
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        assert result.filter.value == 5

    @pytest.mark.asyncio
    async def test_should_not_resolve_when_value_is_none(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
    ) -> None:
        filter = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.IS_EMPTY,
            value=None,
        )
        params = _create_query_params(filter)

        result = await query_resolver.resolve_params(params)

        mock_user_resolver.resolve_name_to_id.assert_not_called()
        assert result.filter.value is None


class TestCompoundFilterResolution:
    @pytest.mark.asyncio
    async def test_should_resolve_all_filters_in_compound_and_filter(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
        mock_page_resolver: PageNameIdResolver,
    ) -> None:
        filter1 = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value="John Doe",
        )
        filter2 = _create_property_filter(
            property_name="Related Tasks",
            property_type=PropertyType.RELATION,
            operator=StringOperator.CONTAINS,
            value="Task Title",
        )
        compound_filter = CompoundFilter(
            operator=LogicalOperator.AND,
            filters=[filter1, filter2],
        )
        params = _create_query_params(compound_filter)

        result = await query_resolver.resolve_params(params)

        mock_user_resolver.resolve_name_to_id.assert_called_once_with("John Doe")
        mock_page_resolver.resolve_name_to_id.assert_called_once_with("Task Title")
        assert result.filter.filters[0].value == "user-uuid-123"
        assert result.filter.filters[1].value == "page-uuid-456"

    @pytest.mark.asyncio
    async def test_should_resolve_nested_compound_filters(
        self,
        query_resolver: QueryResolver,
        mock_user_resolver: PersonNameIdResolver,
        valid_uuid: str,
    ) -> None:
        # OR (
        #   people.contains("John Doe")
        #   AND (
        #     people.contains("Jane Doe")
        #     people.contains(uuid)
        #   )
        # )
        filter1 = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value="John Doe",
        )
        filter2 = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value="Jane Doe",
        )
        filter3 = _create_property_filter(
            property_name="Assigned To",
            property_type=PropertyType.PEOPLE,
            operator=StringOperator.CONTAINS,
            value=valid_uuid,
        )

        inner_and = CompoundFilter(
            operator=LogicalOperator.AND,
            filters=[filter2, filter3],
        )
        outer_or = CompoundFilter(
            operator=LogicalOperator.OR,
            filters=[filter1, inner_and],
        )
        params = _create_query_params(outer_or)

        result = await query_resolver.resolve_params(params)

        # John Doe should be resolved
        assert result.filter.filters[0].value == "user-uuid-123"
        # Jane Doe should be resolved in nested filter
        assert result.filter.filters[1].filters[0].value == "user-uuid-123"
        # UUID should remain unchanged
        assert result.filter.filters[1].filters[1].value == valid_uuid


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_should_raise_error_for_non_string_value_in_people_property(
        self,
        query_resolver: QueryResolver,
    ) -> None:
        # Validation now happens in PropertyFilter creation
        with pytest.raises(ValueError, match="must be a string"):
            _create_property_filter(
                property_name="Assigned To",
                property_type=PropertyType.PEOPLE,
                operator=StringOperator.CONTAINS,
                value=123,  # Invalid: number instead of string
            )

    @pytest.mark.asyncio
    async def test_should_raise_error_for_non_string_value_in_relation_property(
        self,
        query_resolver: QueryResolver,
    ) -> None:
        # Validation now happens in PropertyFilter creation
        with pytest.raises(ValueError, match="must be a string"):
            _create_property_filter(
                property_name="Related Tasks",
                property_type=PropertyType.RELATION,
                operator=StringOperator.CONTAINS,
                value=["not", "a", "string"],  # Invalid: list instead of string
            )
