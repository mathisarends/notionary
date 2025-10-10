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
    NotionFilter,
    NumberOperator,
    PropertyFilter,
    StringOperator,
)
from notionary.exceptions.data_source import DataSourcePropertyNotFound


class DataSourceFilterBuilder:
    def __init__(self, properties: dict[str, DataSourceProperty]) -> None:
        self._filters: list[FilterCondition] = []
        self._current_property: str | None = None
        self._properties = properties or {}

    def where(self, property_name: str) -> Self:
        if self._properties and property_name not in self._properties:
            availble_properties = list(self._properties.keys())
            raise DataSourcePropertyNotFound(
                property_name=property_name,
                available_properties=availble_properties,
            )

        self._current_property = property_name
        return self

    def and_where(self, property_name: str) -> Self:
        return self.where(property_name)

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

    def build(self) -> DataSourceQueryParams:
        if not self._filters:
            return DataSourceQueryParams()

        notion_filter = self._build_notion_filter()
        return DataSourceQueryParams(filter=notion_filter)

    def _build_notion_filter(self) -> NotionFilter:
        if len(self._filters) == 1:
            return self._build_property_filter(self._filters[0])

        property_filters = [self._build_property_filter(filter) for filter in self._filters]
        return CompoundFilter(operator="and", filters=property_filters)

    def _build_property_filter(self, condition: FilterCondition) -> PropertyFilter:
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

        field_type = self._infer_field_type_from_operator(operator)

        filter_condition = FilterCondition(
            field=self._current_property,
            field_type=field_type,
            operator=operator,
            value=value,
        )

        self._filters.append(filter_condition)
        self._current_property = None
        return self

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
