from unittest.mock import Mock

import pytest

from notionary.data_source.data_source import DataSource
from notionary.data_source.data_source_instance_client import (
    DataSourceInstanceClient,
)
from notionary.data_source.exceptions import (
    DataSourcePropertyNotFound,
    DataSourcePropertyTypeError,
)
from notionary.data_source.properties.schemas import (
    DataSourceMultiSelectProperty,
    DataSourcePropertyOption,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.shared.properties.type import PropertyType


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
    test_properties: dict,
) -> DataSource:
    mock_http = Mock()

    return DataSource(
        id="ds-123",
        url="https://notion.so/ds-123",
        title="Test Data Source",
        description="Test description",
        archived=False,
        icon=None,
        cover=None,
        in_trash=False,
        properties=test_properties,
        data_source_instance_client=Mock(spec=DataSourceInstanceClient),
        http=mock_http,
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
    data_source: DataSource,
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
    data_source: DataSource,
) -> None:
    with pytest.raises(DataSourcePropertyTypeError) as exc_info:
        data_source.get_select_options_by_property_name("Tags")

    error_msg = str(exc_info.value)
    assert "Tags" in error_msg
    assert "DataSourceSelectProperty" in error_msg
    assert "DataSourceMultiSelectProperty" in error_msg


def test_property_not_found_raises_error(data_source: DataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source.get_select_options_by_property_name("NonExistent")

    assert "NonExistent" in str(exc_info.value)


def test_property_not_found_includes_suggestions(data_source: DataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        data_source.get_select_options_by_property_name("Priorit")

    assert "Priority" in str(exc_info.value)


def test_case_sensitive_property_lookup(data_source: DataSource) -> None:
    with pytest.raises(DataSourcePropertyNotFound):
        data_source.get_select_options_by_property_name("priority")


def test_properties_getter_returns_all_properties(
    data_source: DataSource,
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
    data_source: DataSource,
    property_name: str,
    expected_options: list[str],
) -> None:
    options = await data_source.get_options_for_property_by_name(property_name)
    assert options == expected_options
