from notionary.data_source.query.filters import (
    CheckboxCondition,
    CheckboxFilter,
    CompoundFilter,
    DateCondition,
    DateFilter,
    MultiSelectCondition,
    MultiSelectFilter,
    NumberCondition,
    NumberFilter,
    QueryFilter,
    RelationCondition,
    RelationFilter,
    RichTextFilter,
    SelectCondition,
    SelectFilter,
    StatusCondition,
    StatusFilter,
    TextCondition,
    TimestampFilter,
    TimestampType,
)


class _TextFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def equals(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(equals=value)
        )

    def does_not_equal(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(does_not_equal=value)
        )

    def contains(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(contains=value)
        )

    def does_not_contain(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(does_not_contain=value)
        )

    def starts_with(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(starts_with=value)
        )

    def ends_with(self, value: str) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(ends_with=value)
        )

    def is_empty(self) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(is_empty=True)
        )

    def is_not_empty(self) -> RichTextFilter:
        return RichTextFilter(
            property=self._prop, rich_text=TextCondition(is_not_empty=True)
        )


class _NumberFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def equals(self, value: int | float) -> NumberFilter:
        return NumberFilter(property=self._prop, number=NumberCondition(equals=value))

    def does_not_equal(self, value: int | float) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(does_not_equal=value)
        )

    def greater_than(self, value: int | float) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(greater_than=value)
        )

    def less_than(self, value: int | float) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(less_than=value)
        )

    def greater_than_or_equal_to(self, value: int | float) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(greater_than_or_equal_to=value)
        )

    def less_than_or_equal_to(self, value: int | float) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(less_than_or_equal_to=value)
        )

    def between(self, low: int | float, high: int | float) -> CompoundFilter:
        return Filter.all(
            NumberFilter(
                property=self._prop,
                number=NumberCondition(greater_than_or_equal_to=low),
            ),
            NumberFilter(
                property=self._prop, number=NumberCondition(less_than_or_equal_to=high)
            ),
        )

    def is_empty(self) -> NumberFilter:
        return NumberFilter(property=self._prop, number=NumberCondition(is_empty=True))

    def is_not_empty(self) -> NumberFilter:
        return NumberFilter(
            property=self._prop, number=NumberCondition(is_not_empty=True)
        )


class _SelectFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def equals(self, value: str) -> SelectFilter:
        return SelectFilter(property=self._prop, select=SelectCondition(equals=value))

    def not_equals(self, value: str) -> SelectFilter:
        return SelectFilter(
            property=self._prop, select=SelectCondition(does_not_equal=value)
        )

    def is_empty(self) -> SelectFilter:
        return SelectFilter(property=self._prop, select=SelectCondition(is_empty=True))

    def is_not_empty(self) -> SelectFilter:
        return SelectFilter(
            property=self._prop, select=SelectCondition(is_not_empty=True)
        )


class _StatusFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def equals(self, value: str) -> StatusFilter:
        return StatusFilter(property=self._prop, status=StatusCondition(equals=value))

    def not_equals(self, value: str) -> StatusFilter:
        return StatusFilter(
            property=self._prop, status=StatusCondition(does_not_equal=value)
        )

    def is_empty(self) -> StatusFilter:
        return StatusFilter(property=self._prop, status=StatusCondition(is_empty=True))

    def is_not_empty(self) -> StatusFilter:
        return StatusFilter(
            property=self._prop, status=StatusCondition(is_not_empty=True)
        )


class _DateFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def equals(self, date: str) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(equals=date))

    def before(self, date: str) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(before=date))

    def after(self, date: str) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(after=date))

    def on_or_before(self, date: str) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(on_or_before=date))

    def on_or_after(self, date: str) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(on_or_after=date))

    def this_week(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(this_week={}))

    def past_week(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(past_week={}))

    def past_month(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(past_month={}))

    def past_year(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(past_year={}))

    def next_week(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(next_week={}))

    def next_month(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(next_month={}))

    def next_year(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(next_year={}))

    def is_empty(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(is_empty=True))

    def is_not_empty(self) -> DateFilter:
        return DateFilter(property=self._prop, date=DateCondition(is_not_empty=True))


class _MultiSelectFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def contains(self, value: str) -> MultiSelectFilter:
        return MultiSelectFilter(
            property=self._prop, multi_select=MultiSelectCondition(contains=value)
        )

    def does_not_contain(self, value: str) -> MultiSelectFilter:
        return MultiSelectFilter(
            property=self._prop,
            multi_select=MultiSelectCondition(does_not_contain=value),
        )

    def contains_all(self, *values: str) -> CompoundFilter:
        return Filter.all(
            *(
                MultiSelectFilter(
                    property=self._prop, multi_select=MultiSelectCondition(contains=v)
                )
                for v in values
            )
        )

    def contains_any(self, *values: str) -> CompoundFilter:
        return Filter.any(
            *(
                MultiSelectFilter(
                    property=self._prop, multi_select=MultiSelectCondition(contains=v)
                )
                for v in values
            )
        )

    def is_empty(self) -> MultiSelectFilter:
        return MultiSelectFilter(
            property=self._prop, multi_select=MultiSelectCondition(is_empty=True)
        )

    def is_not_empty(self) -> MultiSelectFilter:
        return MultiSelectFilter(
            property=self._prop, multi_select=MultiSelectCondition(is_not_empty=True)
        )


class _RelationFilterBuilder:
    def __init__(self, prop: str) -> None:
        self._prop = prop

    def contains(self, page_id: str) -> RelationFilter:
        return RelationFilter(
            property=self._prop, relation=RelationCondition(contains=page_id)
        )

    def does_not_contain(self, page_id: str) -> RelationFilter:
        return RelationFilter(
            property=self._prop, relation=RelationCondition(does_not_contain=page_id)
        )

    def is_empty(self) -> RelationFilter:
        return RelationFilter(
            property=self._prop, relation=RelationCondition(is_empty=True)
        )

    def is_not_empty(self) -> RelationFilter:
        return RelationFilter(
            property=self._prop, relation=RelationCondition(is_not_empty=True)
        )


class Filter:
    """Fluent builder for Notion data source query filters.

    Examples::

        Filter.text("Name").contains("foo")
        Filter.status("Status").equals("Done")
        Filter.checkbox("Active")
        Filter.number("Price").between(10, 50)
        Filter.date("Due").past_week()
        Filter.multi_select("Tags").contains_all("python", "async")

        Filter.all(
            Filter.status("Status").not_equals("Done"),
            Filter.date("Due").this_week(),
        )
    """

    @staticmethod
    def text(property: str) -> _TextFilterBuilder:
        return _TextFilterBuilder(property)

    @staticmethod
    def number(property: str) -> _NumberFilterBuilder:
        return _NumberFilterBuilder(property)

    @staticmethod
    def select(property: str) -> _SelectFilterBuilder:
        return _SelectFilterBuilder(property)

    @staticmethod
    def status(property: str) -> _StatusFilterBuilder:
        return _StatusFilterBuilder(property)

    @staticmethod
    def date(property: str) -> _DateFilterBuilder:
        return _DateFilterBuilder(property)

    @staticmethod
    def multi_select(property: str) -> _MultiSelectFilterBuilder:
        return _MultiSelectFilterBuilder(property)

    @staticmethod
    def relation(property: str) -> _RelationFilterBuilder:
        return _RelationFilterBuilder(property)

    @staticmethod
    def checkbox(property: str, *, checked: bool = True) -> CheckboxFilter:
        return CheckboxFilter(
            property=property, checkbox=CheckboxCondition(equals=checked)
        )

    @staticmethod
    def all(*filters: QueryFilter) -> CompoundFilter:
        return CompoundFilter(and_=list(filters))

    @staticmethod
    def any(*filters: QueryFilter) -> CompoundFilter:
        return CompoundFilter(or_=list(filters))

    @staticmethod
    def created_after(date: str) -> TimestampFilter:
        return TimestampFilter(
            timestamp=TimestampType.CREATED_TIME,
            condition=DateCondition(after=date),
        )

    @staticmethod
    def created_before(date: str) -> TimestampFilter:
        return TimestampFilter(
            timestamp=TimestampType.CREATED_TIME,
            condition=DateCondition(before=date),
        )

    @staticmethod
    def created_this_week() -> TimestampFilter:
        return TimestampFilter(
            timestamp=TimestampType.CREATED_TIME,
            condition=DateCondition(this_week={}),
        )

    @staticmethod
    def edited_after(date: str) -> TimestampFilter:
        return TimestampFilter(
            timestamp=TimestampType.LAST_EDITED_TIME,
            condition=DateCondition(after=date),
        )

    @staticmethod
    def edited_before(date: str) -> TimestampFilter:
        return TimestampFilter(
            timestamp=TimestampType.LAST_EDITED_TIME,
            condition=DateCondition(before=date),
        )
