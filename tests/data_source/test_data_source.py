from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.name_id_resolver.page import PageNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.person import PersonNameIdResolver
from notionary.data_source.http.data_source_instance_client import (
    DataSourceInstanceClient,
)
from notionary.data_source.properties.schemas import (
    DataSourceMultiSelectProperty,
    DataSourcePropertyOption,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.query.resolver import QueryResolver
from notionary.data_source.schemas import DataSourceDto
from notionary.data_source.service import NotionDataSource
from notionary.exceptions.data_source import (
    DataSourcePropertyNotFound,
    DataSourcePropertyTypeError,
)
from notionary.shared.models.parent import PageParent, ParentType, WorkspaceParent
from notionary.shared.properties.type import PropertyType
from notionary.user.schemas import PartialUserDto
from notionary.user.service import UserService


@pytest.fixture
def mock_user() -> PartialUserDto:
    return PartialUserDto(id="user-123", object="user")


@pytest.fixture
def base_dto(mock_user: PartialUserDto) -> DataSourceDto:
    return DataSourceDto(
        object="database",
        id="ds-123",
        created_time="2024-01-01T00:00:00.000Z",
        created_by=mock_user,
        last_edited_time="2024-01-01T00:00:00.000Z",
        last_edited_by=mock_user,
        cover=None,
        icon=None,
        parent=PageParent(type=ParentType.PAGE_ID, page_id="parent-page-123"),
        url="https://notion.so/ds-123",
        public_url=None,
        database_parent=WorkspaceParent(type=ParentType.WORKSPACE, workspace=True),
        title=[],
        description=[],
        archived=False,
        properties={},
        is_inline=False,
        in_trash=False,
    )


@pytest.fixture
def mock_query_resolver() -> QueryResolver:
    return QueryResolver(
        user_resolver=AsyncMock(spec=PersonNameIdResolver),
        page_resolver=AsyncMock(spec=PageNameIdResolver),
    )


@pytest.fixture
def test_properties() -> dict:
    return {
        "Status": DataSourceStatusProperty(
            id="prop-status",
            name="Status",
            type=PropertyType.STATUS,
            status={
                "options": [
                    DataSourcePropertyOption(id="opt-1", name="Todo", color="default"),
                    DataSourcePropertyOption(
                        id="opt-2", name="In Progress", color="blue"
                    ),
                    DataSourcePropertyOption(id="opt-3", name="Done", color="green"),
                ]
            },
        ),
        "Priority": DataSourceSelectProperty(
            id="prop-select",
            name="Priority",
            type=PropertyType.SELECT,
            select={
                "options": [
                    DataSourcePropertyOption(id="opt-4", name="High", color="red"),
                    DataSourcePropertyOption(id="opt-5", name="Medium", color="yellow"),
                    DataSourcePropertyOption(id="opt-6", name="Low", color="gray"),
                ]
            },
        ),
        "Tags": DataSourceMultiSelectProperty(
            id="prop-multi",
            name="Tags",
            type=PropertyType.MULTI_SELECT,
            multi_select={
                "options": [
                    DataSourcePropertyOption(id="opt-7", name="Bug", color="red"),
                    DataSourcePropertyOption(id="opt-8", name="Feature", color="blue"),
                    DataSourcePropertyOption(
                        id="opt-9", name="Documentation", color="green"
                    ),
                ]
            },
        ),
        "Related": DataSourceRelationProperty(
            id="prop-relation",
            name="Related",
            type=PropertyType.RELATION,
            relation={"data_source_id": "db-related-123"},
        ),
        "Description": DataSourceRichTextProperty(
            id="prop-text",
            name="Description",
            type=PropertyType.RICH_TEXT,
        ),
    }


@pytest.fixture
def data_source(
    base_dto: DataSourceDto,
    test_properties: dict,
    mock_query_resolver: QueryResolver,
    monkeypatch,
) -> NotionDataSource:
    from notionary.file_upload.service import NotionFileUpload

    monkeypatch.setattr(
        "notionary.shared.entity.service.UserService", lambda: Mock(spec=UserService)
    )

    mock_file_upload_service = Mock(spec=NotionFileUpload)

    return NotionDataSource(
        dto=base_dto,
        title="Test Data Source",
        description="Test description",
        properties=test_properties,
        data_source_instance_client=Mock(spec=DataSourceInstanceClient),
        query_resolver=mock_query_resolver,
        user_service=Mock(spec=UserService),
        file_upload_service=mock_file_upload_service,
    )


# ============================================================================
# Tests - Synchronous Property Options
# ============================================================================


@pytest.mark.parametrize(
    "property_name,expected_options",
    [
        ("Priority", ["High", "Medium", "Low"]),
        ("Status", ["Todo", "In Progress", "Done"]),
        ("Tags", ["Bug", "Feature", "Documentation"]),
    ],
)
def test_get_options_by_property_type(
    data_source: NotionDataSource,
    property_name: str,
    expected_options: list[str],
) -> None:
    method_map = {
        "Priority": data_source.get_select_options_by_property_name,
        "Status": data_source.get_status_options_by_property_name,
        "Tags": data_source.get_multi_select_options_by_property_name,
    }

    options = method_map[property_name](property_name)
    assert options == expected_options


def test_get_property_with_wrong_type_raises_error(
    data_source: NotionDataSource,
) -> None:
    with pytest.raises(DataSourcePropertyTypeError) as exc_info:
        data_source.get_select_options_by_property_name("Tags")

    error_msg = str(exc_info.value)
    assert "Tags" in error_msg
    assert "DataSourceSelectProperty" in error_msg
    assert "DataSourceMultiSelectProperty" in error_msg


def test_property_not_found_raises_error(data_source: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source.get_select_options_by_property_name("NonExistent")

    assert "NonExistent" in str(exc_info.value)


def test_property_not_found_includes_suggestions(data_source: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source.get_select_options_by_property_name("Priorit")

    assert "Priority" in str(exc_info.value)


def test_case_sensitive_property_lookup(data_source: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound):
        data_source.get_select_options_by_property_name("priority")


def test_properties_getter_returns_all_properties(
    data_source: NotionDataSource,
) -> None:
    properties = data_source.properties

    assert len(properties) == 5
    assert set(properties.keys()) == {
        "Status",
        "Priority",
        "Tags",
        "Related",
        "Description",
    }


# ============================================================================
# Tests - Asynchronous Property Options
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "property_name,expected_options",
    [
        ("Priority", ["High", "Medium", "Low"]),
        ("Tags", ["Bug", "Feature", "Documentation"]),
        ("Status", ["Todo", "In Progress", "Done"]),
        ("Description", []),  # Unsupported type returns empty
        ("NonExistent", []),  # Non-existent returns empty
    ],
)
async def test_get_options_for_property_async(
    data_source: NotionDataSource,
    property_name: str,
    expected_options: list[str],
) -> None:
    options = await data_source.get_options_for_property_by_name(property_name)
    assert options == expected_options
