import pytest

from notionary.data_source.properties.schemas import (
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
from notionary.data_source.query.builder import DataSourceQueryBuilder
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
    PropertySort,
    SortDirection,
    StringOperator,
    TimestampSort,
    TimestampType,
)
from notionary.exceptions.data_source.properties import DataSourcePropertyNotFound
from notionary.shared.properties.type import PropertyType


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
def builder(mock_properties: dict[str, DataSourceProperty]) -> DataSourceQueryBuilder:
    return DataSourceQueryBuilder(properties=mock_properties)


@pytest.fixture
def empty_builder() -> DataSourceQueryBuilder:
    return DataSourceQueryBuilder(properties={})


def test_equals_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.property == "Status"
    assert result.filter.operator == StringOperator.EQUALS
    assert result.filter.value == "Active"


def test_does_not_equal_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Status").does_not_equal("Archived").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.DOES_NOT_EQUAL
    assert result.filter.value == "Archived"


def test_contains_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").contains("important").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.CONTAINS
    assert result.filter.value == "important"


def test_does_not_contain_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").does_not_contain("spam").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.DOES_NOT_CONTAIN


def test_starts_with_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").starts_with("In").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.STARTS_WITH
    assert result.filter.value == "In"


def test_ends_with_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").ends_with("Progress").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.ENDS_WITH


def test_is_empty_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").is_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.IS_EMPTY
    assert result.filter.value is None


def test_is_not_empty_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Description").is_not_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == StringOperator.IS_NOT_EMPTY
    assert result.filter.value is None


# ============================================================================
# Number Operators
# ============================================================================


def test_greater_than_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Price").greater_than(100).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.GREATER_THAN
    assert result.filter.value == 100


def test_greater_than_or_equal_to_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Price").greater_than_or_equal_to(50.5).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.GREATER_THAN_OR_EQUAL_TO
    assert result.filter.value == pytest.approx(50.5)


def test_less_than_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Price").less_than(200).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.LESS_THAN


def test_less_than_or_equal_to_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Price").less_than_or_equal_to(150).build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == NumberOperator.LESS_THAN_OR_EQUAL_TO


# ============================================================================
# Boolean Operators
# ============================================================================


def test_is_true_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Completed").is_true().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == BooleanOperator.IS_TRUE
    assert result.filter.value is None


def test_is_false_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Completed").is_false().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == BooleanOperator.IS_FALSE
    assert result.filter.value is None


# ============================================================================
# Date Operators
# ============================================================================


def test_before_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("2025-12-31").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.BEFORE
    assert result.filter.value == "2025-12-31"


def test_after_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").after("2025-01-01").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.AFTER


def test_on_or_before_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").on_or_before("2025-06-30").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_BEFORE


def test_on_or_after_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").on_or_after("2025-03-01").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_AFTER


# ============================================================================
# Date Format Parsing
# ============================================================================


def test_before_filter_german_format(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("31.12.2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.BEFORE
    assert result.filter.value == "2024-12-31"


def test_after_filter_us_format_slash(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").after("12/25/2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.AFTER
    assert result.filter.value == "2024-12-25"


def test_on_or_before_filter_us_format_dash(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").on_or_before("12-25-2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_BEFORE
    assert result.filter.value == "2024-12-25"


def test_on_or_after_filter_mixed_format_slash(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").on_or_after("25/12/2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.ON_OR_AFTER
    assert result.filter.value == "2024-12-25"


def test_before_filter_text_month_format(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("31-Dec-2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.BEFORE
    assert result.filter.value == "2024-12-31"


def test_after_filter_text_month_with_space(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").after("25 Dec 2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.AFTER
    assert result.filter.value == "2024-12-25"


def test_before_filter_full_month_name(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("31-December-2024").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == DateOperator.BEFORE
    assert result.filter.value == "2024-12-31"


def test_invalid_date_format_raises_error(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(ValueError, match="Invalid date format"):
        builder.where("Due Date").before("invalid-date")


def test_iso_format_still_works(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Due Date").before("2024-12-31").build()

    assert result.filter is not None
    assert result.filter.value == "2024-12-31"


# ============================================================================
# Array Operators
# ============================================================================


def test_array_contains_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Tags").array_contains("urgent").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.CONTAINS
    assert result.filter.value == "urgent"


def test_array_does_not_contain_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Tags").array_does_not_contain("archived").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.DOES_NOT_CONTAIN


def test_array_is_empty_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Tags").array_is_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.IS_EMPTY
    assert result.filter.value is None


def test_array_is_not_empty_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Tags").array_is_not_empty().build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert result.filter.operator == ArrayOperator.IS_NOT_EMPTY


# ============================================================================
# Compound Filters
# ============================================================================


def test_multiple_conditions_with_and_where(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Price")
        .greater_than(100)
        .build()
    )

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


def test_three_conditions_compound_filter(builder: DataSourceQueryBuilder) -> None:
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
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.filter is not None
    assert isinstance(result.filter, PropertyFilter)
    assert not isinstance(result.filter, CompoundFilter)


# ============================================================================
# Error Handling
# ============================================================================


def test_property_not_found_raises_exception(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        builder.where("NonExistentProperty")

    assert exc_info.value.property_name == "NonExistentProperty"


def test_property_not_found_includes_suggestions(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        status_property_with_typo = "Statu"
        builder.where(status_property_with_typo)

    assert "Status" in exc_info.value.suggestions


def test_filter_without_where_raises_value_error(
    builder: DataSourceQueryBuilder,
) -> None:
    with pytest.raises(ValueError, match="No property selected"):
        builder.equals("test")


def test_build_property_filter_validates_property_exists(
    builder: DataSourceQueryBuilder,
) -> None:
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


def test_build_without_filters_returns_empty_params(
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.build()

    assert isinstance(result, DataSourceQueryParams)
    assert result.filter is None


def test_empty_builder_can_add_filters_but_build_requires_properties() -> None:
    empty_builder = DataSourceQueryBuilder(properties={})

    empty_builder._current_property = "AnyProperty"
    empty_builder._add_filter(StringOperator.EQUALS, "test")

    # But build() will fail because property doesn't exist
    with pytest.raises(DataSourcePropertyNotFound):
        empty_builder.build()


# ============================================================================
# Fluent API
# ============================================================================


def test_chaining_multiple_methods(builder: DataSourceQueryBuilder) -> None:
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


def test_current_property_reset_after_filter(builder: DataSourceQueryBuilder) -> None:
    builder.where("Status").equals("Active")

    assert builder._current_property is None


def test_can_chain_multiple_filters_with_property_reset(
    builder: DataSourceQueryBuilder,
) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Price")
        .greater_than(100)
        .build()
    )

    assert result.filter is not None


# ============================================================================
# Sort Tests
# ============================================================================


def test_order_by_property_ascending(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by("Price", SortDirection.ASCENDING).build()

    assert result.sorts is not None
    assert len(result.sorts) == 1
    assert isinstance(result.sorts[0], PropertySort)
    assert result.sorts[0].property == "Price"
    assert result.sorts[0].direction == SortDirection.ASCENDING


def test_order_by_property_descending(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by("Price", SortDirection.DESCENDING).build()

    assert result.sorts is not None
    assert len(result.sorts) == 1
    assert result.sorts[0].direction == SortDirection.DESCENDING


def test_order_by_ascending_shorthand(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by_property_name_ascending("Status").build()

    assert result.sorts is not None
    assert len(result.sorts) == 1
    assert isinstance(result.sorts[0], PropertySort)
    assert result.sorts[0].property == "Status"
    assert result.sorts[0].direction == SortDirection.ASCENDING


def test_order_by_descending_shorthand(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by_property_name_descending("Status").build()

    assert result.sorts is not None
    assert result.sorts[0].direction == SortDirection.DESCENDING


def test_order_by_created_time(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by_created_time_ascending().build()

    assert result.sorts is not None
    assert len(result.sorts) == 1
    assert isinstance(result.sorts[0], TimestampSort)
    assert result.sorts[0].timestamp == TimestampType.CREATED_TIME
    assert result.sorts[0].direction == SortDirection.ASCENDING


def test_order_by_created_time_default_descending(
    builder: DataSourceQueryBuilder,
) -> None:
    result = builder.order_by_created_time_descending().build()

    assert result.sorts is not None
    assert result.sorts[0].direction == SortDirection.DESCENDING


def test_order_by_last_edited_time(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by_last_edited_time_ascending().build()

    assert result.sorts is not None
    assert len(result.sorts) == 1
    assert isinstance(result.sorts[0], TimestampSort)
    assert result.sorts[0].timestamp == TimestampType.LAST_EDITED_TIME
    assert result.sorts[0].direction == SortDirection.ASCENDING


def test_multiple_sorts_nested(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.order_by_property_name_descending("Priority")
        .order_by_property_name_ascending("Status")
        .order_by_created_time_ascending()
        .build()
    )

    assert result.sorts is not None
    assert len(result.sorts) == 3

    assert result.sorts[0].property == "Priority"
    assert result.sorts[0].direction == SortDirection.DESCENDING

    assert result.sorts[1].property == "Status"
    assert result.sorts[1].direction == SortDirection.ASCENDING

    assert isinstance(result.sorts[2], TimestampSort)
    assert result.sorts[2].timestamp == TimestampType.CREATED_TIME


def test_filter_and_sort_combined(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .and_where("Price")
        .greater_than(100)
        .order_by_property_name_descending("Price")
        .order_by_created_time_descending()
        .build()
    )

    assert result.filter is not None
    assert result.sorts is not None
    assert len(result.sorts) == 2
    assert isinstance(result.filter, CompoundFilter)


def test_sort_validates_property_exists(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(DataSourcePropertyNotFound) as exc_info:
        builder.order_by("NonExistentProperty")

    assert exc_info.value.property_name == "NonExistentProperty"


def test_build_without_sorts_returns_none(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.filter is not None
    assert result.sorts is None


def test_build_with_only_sorts_no_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.order_by_property_name_ascending("Price").build()

    assert result.filter is None
    assert result.sorts is not None
    assert len(result.sorts) == 1


def test_sort_serialization(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.order_by_property_name_descending("Price")
        .order_by_created_time_descending()
        .build()
    )

    serialized = result.model_dump()

    assert "sorts" in serialized
    assert len(serialized["sorts"]) == 2
    assert serialized["sorts"][0] == {"property": "Price", "direction": "descending"}
    assert serialized["sorts"][1] == {
        "timestamp": "created_time",
        "direction": "descending",
    }


def test_filter_and_sort_serialization(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .order_by_property_name_ascending("Price")
        .build()
    )

    serialized = result.model_dump()

    assert "filter" in serialized
    assert "sorts" in serialized
    assert serialized["sorts"][0] == {"property": "Price", "direction": "ascending"}


# ============================================================================
# Limit Tests
# ============================================================================


def test_limit_sets_page_size(builder: DataSourceQueryBuilder) -> None:
    result = builder.total_results_limit(10).build()

    assert result.total_results_limit == 10


def test_limit_with_filter(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Status").equals("Active").total_results_limit(25).build()

    assert result.filter is not None
    assert result.total_results_limit == 25


def test_limit_with_sort(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.order_by_property_name_descending("Price")
        .total_results_limit(50)
        .build()
    )

    assert result.sorts is not None
    assert result.total_results_limit == 50


def test_limit_with_filter_and_sort(builder: DataSourceQueryBuilder) -> None:
    result = (
        builder.where("Status")
        .equals("Active")
        .order_by_property_name_descending("Price")
        .total_results_limit(15)
        .build()
    )

    assert result.filter is not None
    assert result.sorts is not None
    assert result.total_results_limit == 15


def test_limit_less_than_one_raises_error(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(ValueError, match="Limit must be at least 1"):
        builder.total_results_limit(0)


def test_limit_negative_raises_error(builder: DataSourceQueryBuilder) -> None:
    with pytest.raises(ValueError, match="Limit must be at least 1"):
        builder.total_results_limit(-5)


def test_limit_exactly_one_is_valid(builder: DataSourceQueryBuilder) -> None:
    result = builder.total_results_limit(1).build()

    assert result.total_results_limit == 1


def test_limit_large_number_is_valid(builder: DataSourceQueryBuilder) -> None:
    result = builder.total_results_limit(100).build()

    assert result.total_results_limit == 100


def test_without_limit_page_size_is_none(builder: DataSourceQueryBuilder) -> None:
    result = builder.where("Status").equals("Active").build()

    assert result.total_results_limit is None
