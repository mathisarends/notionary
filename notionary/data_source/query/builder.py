from collections.abc import Callable
from typing import Self

from notionary.data_source.properties.schemas import DataSourceProperty
from notionary.data_source.query.schema import (
    ArrayOperator,
    BooleanOperator,
    CompoundFilter,
    DataSourceQueryParams,
    DateOperator,
    FieldType,
    FilterCondition,
    InternalFilterCondition,
    LogicalOperator,
    NotionFilter,
    NotionSort,
    NumberOperator,
    Operator,
    OrGroupMarker,
    PropertyFilter,
    PropertySort,
    SortDirection,
    StringOperator,
    TimestampSort,
    TimestampType,
)
from notionary.data_source.query.validator import QueryValidator
from notionary.exceptions.data_source.properties import DataSourcePropertyNotFound
from notionary.utils.date import parse_date


class DataSourceQueryBuilder:
    def __init__(
        self,
        properties: dict[str, DataSourceProperty],
        query_validator: QueryValidator | None = None,
        date_parser: Callable[[str], str] = parse_date,
    ) -> None:
        self._properties = properties
        self._query_validator = query_validator or QueryValidator()
        self._date_parser = date_parser

        self._filters: list[InternalFilterCondition] = []
        self._sorts: list[NotionSort] = []
        self._current_property: str | None = None
        self._negate_next = False
        self._or_group: list[FilterCondition] | None = None
        self._page_size: int | None = None

    def where(self, property_name: str) -> Self:
        self._finalize_current_or_group()
        self._ensure_property_exists(property_name)
        self._select_property_without_negation(property_name)
        return self

    def where_not(self, property_name: str) -> Self:
        self._finalize_current_or_group()
        self._ensure_property_exists(property_name)
        self._select_property_with_negation(property_name)
        return self

    def and_where(self, property_name: str) -> Self:
        return self.where(property_name)

    def and_where_not(self, property_name: str) -> Self:
        return self.where_not(property_name)

    def or_where(self, property_name: str) -> Self:
        self._ensure_or_group_exists()
        self._ensure_property_exists(property_name)
        self._select_property_without_negation(property_name)
        return self

    def or_where_not(self, property_name: str) -> Self:
        self._ensure_or_group_exists()
        self._ensure_property_exists(property_name)
        self._select_property_with_negation(property_name)
        return self

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
        parsed_date = self._date_parser(date)
        return self._add_filter(DateOperator.BEFORE, parsed_date)

    def after(self, date: str) -> Self:
        parsed_date = self._date_parser(date)
        return self._add_filter(DateOperator.AFTER, parsed_date)

    def on_or_before(self, date: str) -> Self:
        parsed_date = self._date_parser(date)
        return self._add_filter(DateOperator.ON_OR_BEFORE, parsed_date)

    def on_or_after(self, date: str) -> Self:
        parsed_date = self._date_parser(date)
        return self._add_filter(DateOperator.ON_OR_AFTER, parsed_date)

    def array_contains(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.CONTAINS, value)

    def array_does_not_contain(self, value: str) -> Self:
        return self._add_filter(ArrayOperator.DOES_NOT_CONTAIN, value)

    def array_is_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_EMPTY, None)

    def array_is_not_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_NOT_EMPTY, None)

    def relation_contains(self, uuid: str) -> Self:
        return self._add_filter(ArrayOperator.CONTAINS, uuid)

    def relation_is_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_EMPTY, None)

    def people_contains(self, uuid: str) -> Self:
        return self._add_filter(ArrayOperator.CONTAINS, uuid)

    def people_is_empty(self) -> Self:
        return self._add_filter(ArrayOperator.IS_EMPTY, None)

    def order_by(self, property_name: str, direction: SortDirection = SortDirection.ASCENDING) -> Self:
        self._ensure_property_exists(property_name)
        sort = PropertySort(property=property_name, direction=direction)
        self._sorts.append(sort)
        return self

    def order_by_property_name_ascending(self, property_name: str) -> Self:
        return self.order_by(property_name, SortDirection.ASCENDING)

    def order_by_property_name_descending(self, property_name: str) -> Self:
        return self.order_by(property_name, SortDirection.DESCENDING)

    def order_by_created_time_ascending(self) -> Self:
        return self._order_by_created_time(SortDirection.ASCENDING)

    def order_by_created_time_descending(self) -> Self:
        return self._order_by_created_time(SortDirection.DESCENDING)

    def _order_by_created_time(self, direction: SortDirection = SortDirection.DESCENDING) -> Self:
        sort = TimestampSort(timestamp=TimestampType.CREATED_TIME, direction=direction)
        self._sorts.append(sort)
        return self

    def order_by_last_edited_time_ascending(self) -> Self:
        return self._order_by_last_edited_time(SortDirection.ASCENDING)

    def order_by_last_edited_time_descending(self) -> Self:
        return self._order_by_last_edited_time(SortDirection.DESCENDING)

    def _order_by_last_edited_time(self, direction: SortDirection = SortDirection.DESCENDING) -> Self:
        sort = TimestampSort(timestamp=TimestampType.LAST_EDITED_TIME, direction=direction)
        self._sorts.append(sort)
        return self

    def limit(self, total_result_limit: int) -> Self:
        if total_result_limit < 1:
            raise ValueError("Limit must be at least 1")
        self._page_size = total_result_limit
        return self

    def build(self) -> DataSourceQueryParams:
        self._finalize_current_or_group()
        notion_filter = self._create_notion_filter_if_needed()
        sorts = self._create_sorts_if_needed()
        return DataSourceQueryParams(filter=notion_filter, sorts=sorts, page_size=self._page_size)

    def _select_property_without_negation(self, property_name: str) -> None:
        self._current_property = property_name
        self._negate_next = False

    def _select_property_with_negation(self, property_name: str) -> None:
        self._current_property = property_name
        self._negate_next = True

    def _ensure_property_exists(self, property_name: str) -> None:
        if self._has_no_properties():
            return

        if self._property_is_unknown(property_name):
            self._raise_property_not_found_error(property_name)

    def _has_no_properties(self) -> bool:
        return not self._properties

    def _property_is_unknown(self, property_name: str) -> bool:
        return property_name not in self._properties

    def _raise_property_not_found_error(self, property_name: str) -> None:
        available_properties = list(self._properties.keys())
        raise DataSourcePropertyNotFound(
            property_name=property_name,
            available_properties=available_properties,
        )

    def _ensure_or_group_exists(self) -> None:
        if self._or_group_is_not_active():
            self._start_new_or_group()

    def _or_group_is_not_active(self) -> bool:
        return self._or_group is None

    def _start_new_or_group(self) -> None:
        self._or_group = []
        self._move_last_filter_to_or_group()

    def _move_last_filter_to_or_group(self) -> None:
        if self._has_no_filters():
            return

        last_filter = self._filters.pop()
        if self._is_regular_filter_condition(last_filter):
            self._or_group.append(last_filter)

    def _has_no_filters(self) -> bool:
        return not self._filters

    def _is_regular_filter_condition(self, filter_item: InternalFilterCondition) -> bool:
        return isinstance(filter_item, FilterCondition)

    def _finalize_current_or_group(self) -> None:
        if self._should_finalize_or_group():
            self._convert_or_group_to_marker()
            self._clear_or_group()

    def _should_finalize_or_group(self) -> bool:
        return self._or_group is not None and len(self._or_group) > 0

    def _convert_or_group_to_marker(self) -> None:
        or_marker = OrGroupMarker(conditions=self._or_group)
        self._filters.append(or_marker)

    def _clear_or_group(self) -> None:
        self._or_group = None

    def _add_filter(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        value: str | int | float | list[str | int | float] | None,
    ) -> Self:
        self._ensure_property_is_selected()
        self._validate_operator_for_current_property(operator)
        final_operator = self._apply_negation_if_needed(operator)
        filter_condition = self._create_filter_condition(final_operator, value)
        self._store_filter_condition(filter_condition)
        self._reset_current_property()
        return self

    def _validate_operator_for_current_property(self, operator: Operator) -> None:
        if not self._current_property or not self._properties:
            return

        property_obj = self._properties.get(self._current_property)
        if property_obj:
            self._query_validator.validate_operator_for_property(self._current_property, property_obj, operator)
        return self

    def _ensure_property_is_selected(self) -> None:
        if self._no_property_is_selected():
            raise ValueError("No property selected. Use .where(property_name) first.")

    def _no_property_is_selected(self) -> bool:
        return self._current_property is None

    def _apply_negation_if_needed(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator:
        if not self._negate_next:
            return operator

        negated_operator = self._negate_operator(operator)
        self._negate_next = False
        return negated_operator

    def _create_filter_condition(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
        value: str | int | float | list[str | int | float] | None,
    ) -> FilterCondition:
        field_type = self._determine_field_type_from_operator(operator)
        return FilterCondition(
            field=self._current_property,
            field_type=field_type,
            operator=operator,
            value=value,
        )

    def _store_filter_condition(self, filter_condition: FilterCondition) -> None:
        if self._or_group_is_active():
            self._or_group.append(filter_condition)
        else:
            self._filters.append(filter_condition)

    def _or_group_is_active(self) -> bool:
        return self._or_group is not None

    def _reset_current_property(self) -> None:
        self._current_property = None

    def _create_notion_filter_if_needed(self) -> NotionFilter | None:
        if self._has_no_filters():
            return None
        return self._build_notion_filter()

    def _create_sorts_if_needed(self) -> list[NotionSort] | None:
        if not self._sorts:
            return None
        return self._sorts

    def _build_notion_filter(self) -> NotionFilter:
        if self._has_single_filter():
            return self._build_single_filter()
        return self._build_compound_and_filter()

    def _has_single_filter(self) -> bool:
        return len(self._filters) == 1

    def _build_single_filter(self) -> NotionFilter:
        return self._build_filter(self._filters[0])

    def _build_compound_and_filter(self) -> CompoundFilter:
        property_filters = [self._build_filter(f) for f in self._filters]
        return CompoundFilter(operator=LogicalOperator.AND, filters=property_filters)

    def _build_filter(self, condition: InternalFilterCondition) -> PropertyFilter | CompoundFilter:
        if isinstance(condition, OrGroupMarker):
            return self._build_or_compound_filter(condition)
        return self._build_property_filter(condition)

    def _build_or_compound_filter(self, or_marker: OrGroupMarker) -> CompoundFilter:
        property_filters = [self._build_property_filter(c) for c in or_marker.conditions]
        return CompoundFilter(operator=LogicalOperator.OR, filters=property_filters)

    def _build_property_filter(self, condition: FilterCondition) -> PropertyFilter:
        property_definition = self._get_property_definition(condition.field)
        return PropertyFilter(
            property=condition.field,
            property_type=property_definition.type,
            operator=condition.operator,
            value=condition.value,
        )

    def _get_property_definition(self, property_name: str) -> DataSourceProperty:
        property_definition = self._properties.get(property_name)
        if property_definition is None:
            self._raise_property_not_found_error(property_name)
        return property_definition

    def _negate_operator(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator:
        negation_map = {
            StringOperator.EQUALS: StringOperator.DOES_NOT_EQUAL,
            StringOperator.DOES_NOT_EQUAL: StringOperator.EQUALS,
            StringOperator.CONTAINS: StringOperator.DOES_NOT_CONTAIN,
            StringOperator.DOES_NOT_CONTAIN: StringOperator.CONTAINS,
            StringOperator.IS_EMPTY: StringOperator.IS_NOT_EMPTY,
            StringOperator.IS_NOT_EMPTY: StringOperator.IS_EMPTY,
            NumberOperator.EQUALS: NumberOperator.DOES_NOT_EQUAL,
            NumberOperator.DOES_NOT_EQUAL: NumberOperator.EQUALS,
            NumberOperator.GREATER_THAN: NumberOperator.LESS_THAN_OR_EQUAL_TO,
            NumberOperator.GREATER_THAN_OR_EQUAL_TO: NumberOperator.LESS_THAN,
            NumberOperator.LESS_THAN: NumberOperator.GREATER_THAN_OR_EQUAL_TO,
            NumberOperator.LESS_THAN_OR_EQUAL_TO: NumberOperator.GREATER_THAN,
            NumberOperator.IS_EMPTY: NumberOperator.IS_NOT_EMPTY,
            NumberOperator.IS_NOT_EMPTY: NumberOperator.IS_EMPTY,
            BooleanOperator.IS_TRUE: BooleanOperator.IS_FALSE,
            BooleanOperator.IS_FALSE: BooleanOperator.IS_TRUE,
            DateOperator.BEFORE: DateOperator.ON_OR_AFTER,
            DateOperator.AFTER: DateOperator.ON_OR_BEFORE,
            DateOperator.ON_OR_BEFORE: DateOperator.AFTER,
            DateOperator.ON_OR_AFTER: DateOperator.BEFORE,
            DateOperator.IS_EMPTY: DateOperator.IS_NOT_EMPTY,
            DateOperator.IS_NOT_EMPTY: DateOperator.IS_EMPTY,
            ArrayOperator.CONTAINS: ArrayOperator.DOES_NOT_CONTAIN,
            ArrayOperator.DOES_NOT_CONTAIN: ArrayOperator.CONTAINS,
            ArrayOperator.IS_EMPTY: ArrayOperator.IS_NOT_EMPTY,
            ArrayOperator.IS_NOT_EMPTY: ArrayOperator.IS_EMPTY,
        }

        if operator not in negation_map:
            self._raise_operator_cannot_be_negated_error(operator)

        return negation_map[operator]

    def _raise_operator_cannot_be_negated_error(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> None:
        raise ValueError(f"Operator '{operator}' cannot be negated. This should not happen - please report this issue.")

    def _determine_field_type_from_operator(
        self,
        operator: StringOperator | NumberOperator | BooleanOperator | DateOperator | ArrayOperator,
    ) -> FieldType:
        if isinstance(operator, StringOperator):
            return FieldType.STRING
        if isinstance(operator, NumberOperator):
            return FieldType.NUMBER
        if isinstance(operator, BooleanOperator):
            return FieldType.BOOLEAN
        if isinstance(operator, DateOperator):
            return FieldType.DATE
        if isinstance(operator, ArrayOperator):
            return FieldType.ARRAY
        return FieldType.STRING
