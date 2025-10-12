import pytest

from notionary.data_source.properties.models import (
    DataSourceMultiSelectProperty,
    DataSourcePropertyOption,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.service import NotionDataSource
from notionary.exceptions.data_source import DataSourcePropertyNotFound, DataSourcePropertyTypeError
from notionary.shared.properties.type import PropertyType
from notionary.user.schemas import PartialUserDto


@pytest.fixture
def mock_user() -> PartialUserDto:
    return PartialUserDto(id="user-123", object="user")


@pytest.fixture
def data_source_with_properties(mock_user: PartialUserDto) -> NotionDataSource:
    """Create a data source with various property types for testing."""
    status_options = [
        DataSourcePropertyOption(id="opt-1", name="Todo", color="default"),
        DataSourcePropertyOption(id="opt-2", name="In Progress", color="blue"),
        DataSourcePropertyOption(id="opt-3", name="Done", color="green"),
    ]

    select_options = [
        DataSourcePropertyOption(id="opt-4", name="High", color="red"),
        DataSourcePropertyOption(id="opt-5", name="Medium", color="yellow"),
        DataSourcePropertyOption(id="opt-6", name="Low", color="gray"),
    ]

    multi_select_options = [
        DataSourcePropertyOption(id="opt-7", name="Bug", color="red"),
        DataSourcePropertyOption(id="opt-8", name="Feature", color="blue"),
        DataSourcePropertyOption(id="opt-9", name="Documentation", color="green"),
    ]

    properties = {
        "Status": DataSourceStatusProperty(
            id="prop-status",
            name="Status",
            type=PropertyType.STATUS,
            status={"options": status_options},
        ),
        "Priority": DataSourceSelectProperty(
            id="prop-select",
            name="Priority",
            type=PropertyType.SELECT,
            select={"options": select_options},
        ),
        "Tags": DataSourceMultiSelectProperty(
            id="prop-multi",
            name="Tags",
            type=PropertyType.MULTI_SELECT,
            multi_select={"options": multi_select_options},
        ),
        "Related": DataSourceRelationProperty(
            id="prop-relation",
            name="Related",
            type=PropertyType.RELATION,
            relation={"database_id": "db-related-123"},
        ),
        "Description": DataSourceRichTextProperty(
            id="prop-text",
            name="Description",
            type=PropertyType.RICH_TEXT,
        ),
    }

    return NotionDataSource(
        id="ds-123",
        title="Test Data Source",
        created_time="2024-01-01T00:00:00.000Z",
        created_by=mock_user,
        last_edited_time="2024-01-01T00:00:00.000Z",
        last_edited_by=mock_user,
        archived=False,
        in_trash=False,
        parent_database_id=None,
        properties=properties,
    )


def test_get_select_options_returns_correct_options(data_source_with_properties: NotionDataSource) -> None:
    options = data_source_with_properties.get_select_options_by_property_name("Priority")

    assert options == ["High", "Medium", "Low"]


def test_get_multi_select_options_returns_correct_options(data_source_with_properties: NotionDataSource) -> None:
    options = data_source_with_properties.get_multi_select_options_by_property_name("Tags")

    assert options == ["Bug", "Feature", "Documentation"]


def test_get_status_options_returns_correct_options(data_source_with_properties: NotionDataSource) -> None:
    options = data_source_with_properties.get_status_options_by_property_name("Status")

    assert options == ["Todo", "In Progress", "Done"]


def test_get_property_with_wrong_type_raises_error(data_source_with_properties: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyTypeError) as exc_info:
        data_source_with_properties.get_select_options_by_property_name("Tags")

    assert "Tags" in str(exc_info.value)
    assert "DataSourceSelectProperty" in str(exc_info.value)
    assert "DataSourceMultiSelectProperty" in str(exc_info.value)


def test_property_not_found_raises_error(data_source_with_properties: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source_with_properties.get_select_options_by_property_name("NonExistent")

    assert "NonExistent" in str(exc_info.value)


def test_property_not_found_with_typo_includes_suggestions(data_source_with_properties: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source_with_properties.get_select_options_by_property_name("Priorit")

    error_message = str(exc_info.value)
    assert "Priority" in error_message


@pytest.mark.asyncio
async def test_get_options_for_property_with_select(data_source_with_properties: NotionDataSource) -> None:
    options = await data_source_with_properties.get_options_for_property_by_name("Priority")

    assert options == ["High", "Medium", "Low"]


@pytest.mark.asyncio
async def test_get_options_for_property_with_multi_select(data_source_with_properties: NotionDataSource) -> None:
    options = await data_source_with_properties.get_options_for_property_by_name("Tags")

    assert options == ["Bug", "Feature", "Documentation"]


@pytest.mark.asyncio
async def test_get_options_for_property_with_status(data_source_with_properties: NotionDataSource) -> None:
    options = await data_source_with_properties.get_options_for_property_by_name("Status")

    assert options == ["Todo", "In Progress", "Done"]


@pytest.mark.asyncio
async def test_get_options_for_unsupported_type_returns_empty(
    data_source_with_properties: NotionDataSource,
) -> None:
    options = await data_source_with_properties.get_options_for_property_by_name("Description")

    assert options == []


@pytest.mark.asyncio
async def test_get_options_for_nonexistent_property_returns_empty(
    data_source_with_properties: NotionDataSource,
) -> None:
    options = await data_source_with_properties.get_options_for_property_by_name("NonExistent")

    assert options == []


def test_properties_getter_returns_all_properties(data_source_with_properties: NotionDataSource) -> None:
    properties = data_source_with_properties.properties

    assert len(properties) == 5
    assert "Status" in properties
    assert "Priority" in properties
    assert "Tags" in properties
    assert "Related" in properties
    assert "Description" in properties


def test_case_sensitive_property_lookup(data_source_with_properties: NotionDataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound):
        data_source_with_properties.get_select_options_by_property_name("priority")
