from typing import Self

from notionary.data_source.properties.models import DataSourceProperty
from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    CompoundFilter,
    DataSourceQueryParams,
    DateOperator,
    FieldType,
    FilterCondition,
    LogicalOperator,
    NotionFilter,
    NotionSort,
    NumberOperator,
    PropertyFilter,
    PropertySort,
    SortDirection,
    StringOperator,
    TimestampSort,
    TimestampType,
)
from notionary.exceptions.data_source import DataSourcePropertyNotFound


class DataSourceQueryBuilder:
    def __init__(self, properties: dict[str, DataSourceProperty]) -> None:
        self._filters: list[FilterCondition] = []
        self._sorts: list[NotionSort] = []
        self._current_property: str | None = None
        self._properties = properties or {}
        self._negate_next = False
        self._or_group: list[FilterCondition] | None = None

    def where(self, property_name: str) -> Self:
        self._validate_property_exists(property_name)

        self._current_property = property_name
        self._negate_next = False
        return self

    def where_not(self, property_name: str) -> Self:
        self._validate_property_exists(property_name)

        self._current_property = property_name
        self._negate_next = True
        return self

    def and_where(self, property_name: str) -> Self:
        return self.where(property_name)

    def and_where_not(self, property_name: str) -> Self:
        return self.where_not(property_name)

    def or_where(self, property_name: str) -> Self:
        if self._or_group is None:
            self._or_group = []

        self._validate_property_exists(property_name)

        self._current_property = property_name
        self._negate_next = False
        return self

    def or_where_not(self, property_name: str) -> Self:
        if self._or_group is None:
            self._or_group = []

        self._validate_property_exists(property_name)

        self._current_property = property_name
        self._negate_next = True
        return self

    def _validate_property_exists(self, property_name: str) -> None:
        if self._properties and property_name not in self._properties:
            available_properties = list(self._properties.keys())
            raise DataSourcePropertyNotFound(
                property_name=property_name,
                available_properties=available_properties,
            )

    def equals(self, value: str | int | float) -> Self:
        return self._add_filter(StringOperator.EQUALS, value)

    def does_not_equal(self, value: str | int | float) -> Self:
        return self._add_filter(StringOperator.DOES_NOT_EQUAL, value)

    def contains(self, value: str) -> Self:
        return self._add_filter(StringOperator.CONTAINS, value)

    def does_not_contain(self, value: str) -> Self:
        return self._add_filter(StringOperator.DOES_NOT_CONTAIN, value)

    def starts_with(self, value: str) -> Self:
        return self._add_filter(StringOperator.STARTS_WITH, value)

    def ends_with(self, value: str) -> Self:
        return self._add_filter(StringOperator.ENDS_WITH, value)

    def is_empty(self) -> Self:
        return self._add_filter(StringOperator.IS_EMPTY, None)

    def is_not_empty(self) -> Self:
        return self._add_filter(StringOperator.IS_NOT_EMPTY, None)

    def greater_than(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.GREATER_THAN, value)

    def greater_than_or_equal_to(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.GREATER_THAN_OR_EQUAL_TO, value)

    def less_than(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.LESS_THAN, value)

    def less_than_or_equal_to(self, value: float | int) -> Self:
        return self._add_filter(NumberOperator.LESS_THAN_OR_EQUAL_TO, value)

    def is_true(self) -> Self:
        return self._add_filter(BooleanOperator.IS_TRUE, None)

    def is_false(self) -> Self:
        return self._add_filter(BooleanOperator.IS_FALSE, None)

    def before(self, date: str) -> Self:
        return self._add_filter(DateOperator.BEFORE, date)

    def after(self, date: str) -> Self:
        return self._add_filter(DateOperator.AFTER, date)

    def on_or_before(self, date: str) -> Self:
        return self._add_filter(DateOperator.ON_OR_BEFORE, date)

    def on_or_after(self, date: str) -> Self:
        return self._add_filter(DateOperator.ON_OR_AFTER, date)

    def array_contains(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.CONTAINS, value)

    def array_does_not_contain(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.DOES_NOT_CONTAIN, value)

    def array_is_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_EMPTY, None)

    def array_is_not_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_NOT_EMPTY, None)

    def order_by(self, property_name: str, direction: SortDirection = SortDirection.ASCENDING) -> Self:
        self._validate_property_exists(property_name)

        self._sorts.append(PropertySort(property=property_name, direction=direction))
        return self

    def order_by_ascending(self, property_name: str) -> Self:
        return self.order_by(property_name, SortDirection.ASCENDING)

    def order_by_descending(self, property_name: str) -> Self:
        return self.order_by(property_name, SortDirection.DESCENDING)

    def order_by_created_time(self, direction: SortDirection = SortDirection.DESCENDING) -> Self:
        self._sorts.append(TimestampSort(timestamp=TimestampType.CREATED_TIME, direction=direction))
        return self

    def order_by_last_edited_time(self, direction: SortDirection = SortDirection.DESCENDING) -> Self:
        self._sorts.append(TimestampSort(timestamp=TimestampType.LAST_EDITED_TIME, direction=direction))
        return self

    def build(self) -> DataSourceQueryParams:
        self._close_or_group()

        notion_filter = self._build_notion_filter() if self._filters else None
        sorts = self._sorts if self._sorts else None

        return DataSourceQueryParams(filter=notion_filter, sorts=sorts)

    def _build_notion_filter(self) -> NotionFilter:
        if len(self._filters) == 1:
            return self._build_property_filter(self._filters[0])

        property_filters = [self._build_property_filter(filter) for filter in self._filters]
        return CompoundFilter(operator=LogicalOperator.AND, filters=property_filters)

    def _build_property_filter(self, condition: FilterCondition) -> PropertyFilter:
        if hasattr(condition, "_is_or_group") and condition._is_or_group:
            # This is a pseudo-condition that contains OR group filters
            or_filters = getattr(condition, "_or_filters", [])
            property_filters = [self._build_single_property_filter(f) for f in or_filters]
            return CompoundFilter(operator=LogicalOperator.OR, filters=property_filters)

        return self._build_single_property_filter(condition)

    def _build_single_property_filter(self, condition: FilterCondition) -> PropertyFilter:
        prop = self._properties.get(condition.field)
        if not prop:
            raise DataSourcePropertyNotFound(
                property_name=condition.field,
                available_properties=list(self._properties.keys()),
            )

        return PropertyFilter(
            property=condition.field,
            property_type=prop.type,
            operator=condition.operator,
            value=condition.value,
        )

    def _add_filter(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        value: str | int | float | list[str | int | float] | None,
    ) -> Self:
        if self._current_property is None:
            raise ValueError("No property selected. Use .where(property_name) first.")

        # Apply negation if needed
        if self._negate_next:
            operator = self._negate_operator(operator)
            self._negate_next = False

        field_type = self._infer_field_type_from_operator(operator)

        filter_condition = FilterCondition(
            field=self._current_property,
            field_type=field_type,
            operator=operator,
            value=value,
        )

        # Add to OR group if active, otherwise to main filters
        if self._or_group is not None:
            self._or_group.append(filter_condition)
        else:
            self._filters.append(filter_condition)

        self._current_property = None
        return self

    def _close_or_group(self) -> None:
        if self._or_group is not None and len(self._or_group) > 0:
            # Create a pseudo-condition to mark this as an OR group
            or_group_marker = FilterCondition(
                field="__or_group__",
                field_type=FieldType.STRING,
                operator=StringOperator.EQUALS,
                value=None,
            )
            # Add metadata to identify this as an OR group
            or_group_marker._is_or_group = True
            or_group_marker._or_filters = self._or_group

            self._filters.append(or_group_marker)
            self._or_group = None

    def _negate_operator(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator:
        negation_map = {
            # String operators
            StringOperator.EQUALS: StringOperator.DOES_NOT_EQUAL,
            StringOperator.DOES_NOT_EQUAL: StringOperator.EQUALS,
            StringOperator.CONTAINS: StringOperator.DOES_NOT_CONTAIN,
            StringOperator.DOES_NOT_CONTAIN: StringOperator.CONTAINS,
            StringOperator.IS_EMPTY: StringOperator.IS_NOT_EMPTY,
            StringOperator.IS_NOT_EMPTY: StringOperator.IS_EMPTY,
            # Number operators
            NumberOperator.EQUALS: NumberOperator.DOES_NOT_EQUAL,
            NumberOperator.DOES_NOT_EQUAL: NumberOperator.EQUALS,
            NumberOperator.GREATER_THAN: NumberOperator.LESS_THAN_OR_EQUAL_TO,
            NumberOperator.GREATER_THAN_OR_EQUAL_TO: NumberOperator.LESS_THAN,
            NumberOperator.LESS_THAN: NumberOperator.GREATER_THAN_OR_EQUAL_TO,
            NumberOperator.LESS_THAN_OR_EQUAL_TO: NumberOperator.GREATER_THAN,
            NumberOperator.IS_EMPTY: NumberOperator.IS_NOT_EMPTY,
            NumberOperator.IS_NOT_EMPTY: NumberOperator.IS_EMPTY,
            # Boolean operators
            BooleanOperator.IS_TRUE: BooleanOperator.IS_FALSE,
            BooleanOperator.IS_FALSE: BooleanOperator.IS_TRUE,
            # Date operators
            DateOperator.BEFORE: DateOperator.ON_OR_AFTER,
            DateOperator.AFTER: DateOperator.ON_OR_BEFORE,
            DateOperator.ON_OR_BEFORE: DateOperator.AFTER,
            DateOperator.ON_OR_AFTER: DateOperator.BEFORE,
            DateOperator.IS_EMPTY: DateOperator.IS_NOT_EMPTY,
            DateOperator.IS_NOT_EMPTY: DateOperator.IS_EMPTY,
            # Array operators
            ArrayOperator.CONTAINS: ArrayOperator.DOES_NOT_CONTAIN,
            ArrayOperator.DOES_NOT_CONTAIN: ArrayOperator.CONTAINS,
            ArrayOperator.IS_EMPTY: ArrayOperator.IS_NOT_EMPTY,
            ArrayOperator.IS_NOT_EMPTY: ArrayOperator.IS_EMPTY,
        }

        if operator in negation_map:
            return negation_map[operator]

        raise ValueError(f"Operator '{operator}' cannot be negated. This should not happen - please report this issue.")

    def _infer_field_type_from_operator(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> FieldType:
        if isinstance(operator, StringOperator):
            return FieldType.STRING
        elif isinstance(operator, NumberOperator):
            return FieldType.NUMBER
        elif isinstance(operator, BooleanOperator):
            return FieldType.BOOLEAN
        elif isinstance(operator, DateOperator):
            return FieldType.DATE
        elif isinstance(operator, ArrayOperator):
            return FieldType.ARRAY

        return FieldType.STRING
