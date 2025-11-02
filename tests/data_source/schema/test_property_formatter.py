from typing import cast
from unittest.mock import AsyncMock

import pytest

from notionary.data_source.properties.schemas import (
    DataSourceMultiSelectConfig,
    DataSourceMultiSelectProperty,
    DataSourcePropertyOption,
    DataSourceRelationConfig,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectConfig,
    DataSourceSelectProperty,
    DataSourceStatusConfig,
    DataSourceStatusProperty,
    PropertyColor,
)
from notionary.data_source.schema.service import PropertyFormatter
from notionary.shared.name_id_resolver import DataSourceNameIdResolver
from notionary.shared.properties.type import PropertyType


@pytest.fixture
def mock_relation_fetcher():
    async def fetcher(prop):
        return ["Entry 1", "Entry 2", "Entry 3"]

    return AsyncMock(side_effect=fetcher)


@pytest.fixture
def mock_data_source_resolver():
    mock = AsyncMock(spec=DataSourceNameIdResolver)
    resolver = cast(DataSourceNameIdResolver, mock)
    resolver.resolve_id_to_name = AsyncMock(return_value="Related Database Name")
    return resolver


@pytest.fixture
def formatter(mock_relation_fetcher, mock_data_source_resolver):
    return PropertyFormatter(
        relation_options_fetcher=mock_relation_fetcher,
        data_source_resolver=mock_data_source_resolver,
    )


@pytest.fixture
def select_property():
    return DataSourceSelectProperty(
        id="select-1",
        name="Status",
        type=PropertyType.SELECT,
        select=DataSourceSelectConfig(
            options=[
                DataSourcePropertyOption(
                    id="opt-1", name="Todo", color=PropertyColor.DEFAULT
                ),
                DataSourcePropertyOption(
                    id="opt-2", name="In Progress", color=PropertyColor.BLUE
                ),
                DataSourcePropertyOption(
                    id="opt-3", name="Done", color=PropertyColor.GREEN
                ),
            ]
        ),
    )


@pytest.fixture
def multi_select_property():
    return DataSourceMultiSelectProperty(
        id="multi-1",
        name="Tags",
        type=PropertyType.MULTI_SELECT,
        multi_select=DataSourceMultiSelectConfig(
            options=[
                DataSourcePropertyOption(
                    id="opt-1", name="Important", color=PropertyColor.RED
                ),
                DataSourcePropertyOption(
                    id="opt-2", name="Urgent", color=PropertyColor.ORANGE
                ),
                DataSourcePropertyOption(
                    id="opt-3", name="Review", color=PropertyColor.YELLOW
                ),
            ]
        ),
    )


@pytest.fixture
def status_property():
    return DataSourceStatusProperty(
        id="status-1",
        name="Project Status",
        type=PropertyType.STATUS,
        status=DataSourceStatusConfig(
            options=[
                DataSourcePropertyOption(
                    id="opt-1", name="Not Started", color=PropertyColor.GRAY
                ),
                DataSourcePropertyOption(
                    id="opt-2", name="Active", color=PropertyColor.BLUE
                ),
                DataSourcePropertyOption(
                    id="opt-3", name="Completed", color=PropertyColor.GREEN
                ),
            ]
        ),
    )


@pytest.fixture
def relation_property():
    return DataSourceRelationProperty(
        id="relation-1",
        name="Related Items",
        type=PropertyType.RELATION,
        relation=DataSourceRelationConfig(data_source_id="db-123"),
    )


@pytest.fixture
def rich_text_property():
    return DataSourceRichTextProperty(
        id="text-1",
        name="Notes",
        type=PropertyType.RICH_TEXT,
    )


@pytest.fixture
def rich_text_property_with_description():
    return DataSourceRichTextProperty(
        id="text-2",
        name="Description",
        type=PropertyType.RICH_TEXT,
        description="Custom notes field",
    )


@pytest.mark.asyncio
async def test_format_select_property_shows_available_options(
    formatter: PropertyFormatter, select_property: DataSourceSelectProperty
):
    result = await formatter.format_property(select_property)

    assert len(result) > 0
    assert any("Choose one option from" in line for line in result)
    assert any("Todo" in line and "Done" in line for line in result)


@pytest.mark.asyncio
async def test_format_multi_select_property_shows_multiple_options(
    formatter: PropertyFormatter, multi_select_property: DataSourceMultiSelectProperty
):
    result = await formatter.format_property(multi_select_property)

    assert len(result) > 0
    assert any("Choose multiple options from" in line for line in result)
    assert any("Important" in line and "Review" in line for line in result)


@pytest.mark.asyncio
async def test_format_status_property_shows_statuses(
    formatter: PropertyFormatter, status_property: DataSourceStatusProperty
):
    result = await formatter.format_property(status_property)

    assert len(result) > 0
    assert any("Available statuses" in line for line in result)
    assert any("Not Started" in line and "Completed" in line for line in result)


@pytest.mark.asyncio
async def test_format_relation_property_shows_linked_database(
    formatter: PropertyFormatter,
    relation_property: DataSourceRelationProperty,
    mock_data_source_resolver,
):
    result = await formatter.format_property(relation_property)

    assert len(result) > 0
    assert any("Links to datasource" in line for line in result)
    mock_data_source_resolver.resolve_id_to_name.assert_called_once_with("db-123")


@pytest.mark.asyncio
async def test_format_relation_property_shows_available_entries(
    formatter: PropertyFormatter,
    relation_property: DataSourceRelationProperty,
    mock_relation_fetcher,
):
    result = await formatter.format_property(relation_property)

    assert any("Available entries" in line for line in result)
    assert any("Entry 1" in line and "Entry 2" in line for line in result)
    mock_relation_fetcher.assert_called_once()


@pytest.mark.asyncio
async def test_format_relation_property_handles_fetch_error_gracefully(
    mock_data_source_resolver,
):
    failing_fetcher = AsyncMock(side_effect=Exception("Fetch failed"))

    formatter = PropertyFormatter(
        relation_options_fetcher=failing_fetcher,
        data_source_resolver=mock_data_source_resolver,
    )

    relation_prop = DataSourceRelationProperty(
        id="relation-1",
        name="Related Items",
        type=PropertyType.RELATION,
        relation=DataSourceRelationConfig(data_source_id="db-123"),
    )

    result = await formatter.format_property(relation_prop)

    assert any("Links to datasource" in line for line in result)
    assert not any("Available entries" in line for line in result)


@pytest.mark.asyncio
async def test_format_standard_property_uses_registry_descriptor(
    formatter: PropertyFormatter, rich_text_property: DataSourceRichTextProperty
):
    result = await formatter.format_property(rich_text_property)

    assert any("Free-form text field" in line for line in result)


@pytest.mark.asyncio
async def test_format_property_includes_custom_description(
    formatter: PropertyFormatter,
    rich_text_property_with_description: DataSourceRichTextProperty,
):
    result = await formatter.format_property(rich_text_property_with_description)

    assert any("Description: Custom notes field" in line for line in result)


@pytest.mark.asyncio
async def test_format_property_excludes_custom_description_when_none(
    formatter: PropertyFormatter, rich_text_property: DataSourceRichTextProperty
):
    result = await formatter.format_property(rich_text_property)

    assert not any(line.startswith("   - Description:") for line in result)
