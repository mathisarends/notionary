from typing import cast
from unittest.mock import AsyncMock

import pytest

from notionary.data_source.properties.schemas import (
    DataSourceNumberConfig,
    DataSourceNumberProperty,
    DataSourceProperty,
    DataSourcePropertyOption,
    DataSourceRelationConfig,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectConfig,
    DataSourceSelectProperty,
    NumberFormat,
    PropertyColor,
)
from notionary.data_source.schema.service import DataSourcePropertySchemaFormatter
from notionary.shared.name_id_resolver import DataSourceNameIdResolver
from notionary.shared.properties.type import PropertyType


@pytest.fixture
def mock_relation_fetcher() -> AsyncMock:
    async def fetcher(prop):
        return ["Entry 1", "Entry 2"]

    return AsyncMock(side_effect=fetcher)


@pytest.fixture
def mock_relation_fetcher_empty() -> AsyncMock:
    async def fetcher(prop):
        return []

    return AsyncMock(side_effect=fetcher)


@pytest.fixture
def mock_data_source_resolver() -> AsyncMock:
    mock_obj = AsyncMock(spec=DataSourceNameIdResolver)
    resolver = cast(DataSourceNameIdResolver, mock_obj)
    resolver.resolve_id_to_name = AsyncMock(return_value="Related DB")
    return resolver


@pytest.fixture
def mock_data_source_resolver_no_name() -> AsyncMock:
    mock_obj = AsyncMock(spec=DataSourceNameIdResolver)
    resolver = cast(DataSourceNameIdResolver, mock_obj)
    resolver.resolve_id_to_name = AsyncMock(return_value=None)
    return resolver


@pytest.fixture
def schema_formatter(
    mock_relation_fetcher: AsyncMock, mock_data_source_resolver: AsyncMock
) -> DataSourcePropertySchemaFormatter:
    return DataSourcePropertySchemaFormatter(
        relation_options_fetcher=mock_relation_fetcher,
        data_source_resolver=mock_data_source_resolver,
    )


@pytest.fixture
def sample_properties() -> dict[str, DataSourceProperty]:
    return {
        "Title": DataSourceProperty(
            id="title-1",
            name="Title",
            type=PropertyType.TITLE,
        ),
        "Status": DataSourceSelectProperty(
            id="status-1",
            name="Status",
            type=PropertyType.SELECT,
            select=DataSourceSelectConfig(
                options=[
                    DataSourcePropertyOption(
                        id="opt-1", name="Todo", color=PropertyColor.DEFAULT
                    ),
                    DataSourcePropertyOption(
                        id="opt-2", name="Done", color=PropertyColor.GREEN
                    ),
                ]
            ),
        ),
        "Notes": DataSourceRichTextProperty(
            id="notes-1",
            name="Notes",
            type=PropertyType.RICH_TEXT,
        ),
    }


@pytest.mark.asyncio
async def test_format_includes_data_source_title(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "Data Source: My Database" in result


@pytest.mark.asyncio
async def test_format_includes_description_when_present(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database",
        description="This is a test database",
        properties=sample_properties,
    )

    assert "Description: This is a test database" in result


@pytest.mark.asyncio
async def test_format_excludes_description_when_none(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "Description:" not in result


@pytest.mark.asyncio
async def test_format_includes_properties_header(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "Properties:" in result


@pytest.mark.asyncio
async def test_format_sorts_properties_with_title_first(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    lines = result.split("\n")
    property_lines = [
        line
        for line in lines
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3.")
    ]

    assert len(property_lines) == 3
    assert "Title" in property_lines[0]


@pytest.mark.asyncio
async def test_format_numbers_properties_sequentially(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "1. - Property Name:" in result
    assert "2. - Property Name:" in result
    assert "3. - Property Name:" in result


@pytest.mark.asyncio
async def test_format_shows_property_names_and_types(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "Property Name: 'Title'" in result
    assert "Property Type: 'title'" in result
    assert "Property Name: 'Status'" in result
    assert "Property Type: 'select'" in result


@pytest.mark.asyncio
async def test_format_includes_empty_lines_between_properties(
    schema_formatter: DataSourcePropertySchemaFormatter,
    sample_properties: dict[str, DataSourceProperty],
):
    result = await schema_formatter.format(
        title="My Database", description=None, properties=sample_properties
    )

    assert "\n\n" in result


@pytest.mark.asyncio
async def test_format_with_empty_properties_dict(
    schema_formatter: DataSourcePropertySchemaFormatter,
):
    result = await schema_formatter.format(
        title="Empty Database", description=None, properties={}
    )

    assert "Data Source: Empty Database" in result
    assert "Properties:" in result
    assert "1. - Property Name:" not in result


@pytest.mark.asyncio
async def test_full_schema_format_structure(
    schema_formatter: DataSourcePropertySchemaFormatter,
):
    properties = {
        "Title": DataSourceProperty(
            id="title-1",
            name="Title",
            type=PropertyType.TITLE,
        ),
        "Count": DataSourceNumberProperty(
            id="count-1",
            name="Count",
            type=PropertyType.NUMBER,
            description="Number of items",
            number=DataSourceNumberConfig(format=NumberFormat.NUMBER),
        ),
    }

    result = await schema_formatter.format(
        title="Test Database",
        description="A database for testing",
        properties=properties,
    )

    assert result.startswith("Data Source: Test Database")
    lines = result.split("\n")

    assert lines[0] == "Data Source: Test Database"
    assert lines[1] == ""
    assert lines[2] == "Description: A database for testing"
    assert lines[3] == ""
    assert lines[4] == "Properties:"
    assert lines[5] == ""
    assert "1. - Property Name: 'Title'" in result
    assert "Description: Number of items" in result


@pytest.mark.asyncio
async def test_format_property_with_multiline_description(
    schema_formatter: DataSourcePropertySchemaFormatter,
):
    properties = {
        "Notes": DataSourceRichTextProperty(
            id="text-1",
            name="Notes",
            type=PropertyType.RICH_TEXT,
            description="This is a long description\nthat spans multiple lines\nand should be handled properly",
        ),
    }

    result = await schema_formatter.format(
        title="Test", description=None, properties=properties
    )

    assert "Description:" in result


@pytest.mark.asyncio
async def test_schema_formatter_preserves_property_order_after_title(
    schema_formatter: DataSourcePropertySchemaFormatter,
):
    properties = {
        "Zebra": DataSourceRichTextProperty(
            id="z", name="Zebra", type=PropertyType.RICH_TEXT
        ),
        "Title": DataSourceProperty(id="t", name="Title", type=PropertyType.TITLE),
        "Alpha": DataSourceRichTextProperty(
            id="a", name="Alpha", type=PropertyType.RICH_TEXT
        ),
        "Beta": DataSourceRichTextProperty(
            id="b", name="Beta", type=PropertyType.RICH_TEXT
        ),
    }

    result = await schema_formatter.format(
        title="Sorted DB", description=None, properties=properties
    )

    lines = [line for line in result.split("\n") if "Property Name:" in line]
    names = [line.split("'")[1] for line in lines]

    assert names[0] == "Title"
    assert names[1:] == sorted(names[1:])


@pytest.mark.asyncio
async def test_format_relation_property_shows_linked_database(
    schema_formatter: DataSourcePropertySchemaFormatter,
):
    properties = {
        "Related": DataSourceRelationProperty(
            id="rel-1",
            name="Related Items",
            type=PropertyType.RELATION,
            relation=DataSourceRelationConfig(data_source_id="db-123"),
        ),
    }

    result = await schema_formatter.format(
        title="Test", description=None, properties=properties
    )

    assert "Links to datasource" in result
    assert "Related DB" in result
