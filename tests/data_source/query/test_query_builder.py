import pytest

from notionary.data_source.properties.models import (
    DataSourceCheckboxProperty,
    DataSourceDateProperty,
    DataSourceMultiSelectProperty,
    DataSourceNumberConfig,
    DataSourceNumberProperty,
    DataSourceProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
    NumberFormat,
)
from notionary.data_source.query.builder import DataSourceFilterBuilder
from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    CompoundFilter,
    DataSourceQueryParams,
    DateOperator,
    FieldType,
    FilterCondition,
    NumberOperator,
    PropertyFilter,
    StringOperator,
)
from notionary.exceptions.data_source import DataSourcePropertyNotFound
from notionary.shared.properties.property_type import PropertyType


@pytest.fixture
def mock_properties() -> dict[str, DataSourceProperty]:
    return {
        "Status": DataSourceStatusProperty(
            id="prop_status",
            name="Status",
            type=PropertyType.STATUS,
        ),
        "Priority": DataSourceSelectProperty(
            id="prop_priority",
            name="Priority",
            type=PropertyType.SELECT,
        ),
        "Tags": DataSourceMultiSelectProperty(
            id="prop_tags",
            name="Tags",
            type=PropertyType.MULTI_SELECT,
        ),
        "Price": DataSourceNumberProperty(
            id="prop_price",
            name="Price",
            type=PropertyType.NUMBER,
            number=DataSourceNumberConfig(format=NumberFormat.DOLLAR),
        ),
        "Completed": DataSourceCheckboxProperty(
            id="prop_completed",
            name="Completed",
            type=PropertyType.CHECKBOX,
        ),
        "Due Date": DataSourceDateProperty(
            id="prop_due_date",
            name="Due Date",
            type=PropertyType.DATE,
        ),
        "Description": DataSourceRichTextProperty(
            id="prop_description",
            name="Description",
            type=PropertyType.RICH_TEXT,
        ),
    }


@pytest.fixture
def builder(mock_properties: dict[str, DataSourceProperty]) -> DataSourceFilterBuilder:
    return DataSourceFilterBuilder(properties=mock_properties)


@pytest.fixture
def empty_builder() -> DataSourceFilterBuilder:
    return DataSourceFilterBuilder(properties={})


def test_equals_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.property == "Status"
    assert result.filter.operator == StringOperator.EQUALS
    assert result.filter.value == "Active"


def test_does_not_equal_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").does_not_equal("Archived").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.DOES_NOT_EQUAL
    assert result.filter.value == "Archived"


def test_contains_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Description").contains("important").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.CONTAINS
    assert result.filter.value == "important"


def test_does_not_contain_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Description").does_not_contain("spam").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.DOES_NOT_CONTAIN


def test_starts_with_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").starts_with("In").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.STARTS_WITH
    assert result.filter.value == "In"


def test_ends_with_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").ends_with("Progress").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.ENDS_WITH


def test_is_empty_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Description").is_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.IS_EMPTY
    assert result.filter.value is None


def test_is_not_empty_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Description").is_not_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.IS_NOT_EMPTY
    assert result.filter.value is None


# ============================================================================
# Number Operators
# ============================================================================


def test_greater_than_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Price").greater_than(100).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.GREATER_THAN
    assert result.filter.value == 100


def test_greater_than_or_equal_to_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Price").greater_than_or_equal_to(50.5).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.GREATER_THAN_OR_EQUAL_TO
    assert result.filter.value == pytest.approx(50.5)


def test_less_than_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Price").less_than(200).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.LESS_THAN


def test_less_than_or_equal_to_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Price").less_than_or_equal_to(150).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.LESS_THAN_OR_EQUAL_TO


# ============================================================================
# Boolean Operators
# ============================================================================


def test_is_true_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Completed").is_true().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == BooleanOperator.IS_TRUE
    assert result.filter.value is None


def test_is_false_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Completed").is_false().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == BooleanOperator.IS_FALSE
    assert result.filter.value is None


# ============================================================================
# Date Operators
# ============================================================================


def test_before_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Due Date").before("2025-12-31").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.BEFORE
    assert result.filter.value == "2025-12-31"


def test_after_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Due Date").after("2025-01-01").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.AFTER


def test_on_or_before_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Due Date").on_or_before("2025-06-30").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_BEFORE


def test_on_or_after_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Due Date").on_or_after("2025-03-01").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_AFTER


# ============================================================================
# Array Operators
# ============================================================================


def test_array_contains_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Tags").array_contains("urgent").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.CONTAINS
    assert result.filter.value == "urgent"


def test_array_does_not_contain_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Tags").array_does_not_contain("archived").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.DOES_NOT_CONTAIN


def test_array_is_empty_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Tags").array_is_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.IS_EMPTY
    assert result.filter.value is None


def test_array_is_not_empty_filter(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Tags").array_is_not_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.IS_NOT_EMPTY


# ============================================================================
# Compound Filters
# ============================================================================


def test_multiple_conditions_with_and_where(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").equals("Active").and_where("Price").greater_than(100).build()

    assert result.filter is not None
    assert isinstance(result.filter, CompoundFilter)
    assert result.filter.operator == "and"
    assert len(result.filter.filters) == 2

    first_filter = result.filter.filters[0]
    second_filter = result.filter.filters[1]

    assert isinstance(first_filter, PropertyFilter)
    assert first_filter.property == "Status"
    assert first_filter.operator == StringOperator.EQUALS

    assert isinstance(second_filter, PropertyFilter)
    assert second_filter.property == "Price"
    assert second_filter.operator == NumberOperator.GREATER_THAN


def test_three_conditions_compound_filter(builder: DataSourceFilterBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Completed")
        .is_true()
        .and_where("Price")
        .less_than(500)
        .build()
    )

    assert result.filter is not None
    assert isinstance(result.filter, CompoundFilter)
    assert len(result.filter.filters) == 3


def test_single_condition_returns_property_filter_not_compound(
    builder: DataSourceFilterBuilder,
) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert not isinstance(result.filter, CompoundFilter)


# ============================================================================
# Error Handling
# ============================================================================


def test_property_not_found_raises_exception(builder: DataSourceFilterBuilder) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        builder.where("NonExistentProperty")

    assert exc_info.value.property_name == "NonExistentProperty"


def test_property_not_found_includes_suggestions(builder: DataSourceFilterBuilder) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        status_property_with_typo = "Statu"
        builder.where(status_property_with_typo)

    assert "Status" in exc_info.value.suggestions


def test_filter_without_where_raises_value_error(builder: DataSourceFilterBuilder) -> None:
    with pytest.raises(ValueError, match="No property selected"):
        builder.equals("test")


def test_build_property_filter_validates_property_exists(builder: DataSourceFilterBuilder) -> None:
    builder._filters.append(
        FilterCondition(
            field="InvalidProperty",
            field_type=FieldType.STRING,
            operator=StringOperator.EQUALS,
            value="test",
        )
    )

    with pytest.raises(DataSourcePropertyNotFound):
        builder.build()


# ============================================================================
# Empty Builds
# ============================================================================


def test_build_without_filters_returns_empty_params(builder: DataSourceFilterBuilder) -> None:
    result = builder.build()

    assert isinstance(result, DataSourceQueryParams)
    assert result.filter is None


def test_empty_builder_can_add_filters_but_build_requires_properties() -> None:
    empty_builder = DataSourceFilterBuilder(properties={})

    empty_builder._current_property = "AnyProperty"
    empty_builder._add_filter(StringOperator.EQUALS, "test")

    # But build() will fail because property doesn't exist
    with pytest.raises(DataSourcePropertyNotFound):
        empty_builder.build()


# ============================================================================
# Fluent API
# ============================================================================


def test_chaining_multiple_methods(builder: DataSourceFilterBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Price")
        .greater_than(100)
        .and_where("Completed")
        .is_true()
        .build()
    )

    assert isinstance(result, DataSourceQueryParams)
    assert result.filter is not None


# ============================================================================
# Property Reset
# ============================================================================


def test_current_property_reset_after_filter(builder: DataSourceFilterBuilder) -> None:
    builder.where("Status").equals("Active")

    assert builder._current_property is None


def test_can_chain_multiple_filters_with_property_reset(builder: DataSourceFilterBuilder) -> None:
    result = builder.where("Status").equals("Active").and_where("Price").greater_than(100).build()

    assert result.filter is not None
