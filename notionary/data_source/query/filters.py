from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_serializer


class TextCondition(BaseModel):
    equals: str | None = None
    does_not_equal: str | None = None
    contains: str | None = None
    does_not_contain: str | None = None
    starts_with: str | None = None
    ends_with: str | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class NumberCondition(BaseModel):
    equals: int | float | None = None
    does_not_equal: int | float | None = None
    greater_than: int | float | None = None
    less_than: int | float | None = None
    greater_than_or_equal_to: int | float | None = None
    less_than_or_equal_to: int | float | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class CheckboxCondition(BaseModel):
    equals: bool | None = None
    does_not_equal: bool | None = None


class SelectCondition(BaseModel):
    equals: str | list[str] | None = None
    does_not_equal: str | list[str] | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class MultiSelectCondition(BaseModel):
    contains: str | list[str] | None = None
    does_not_contain: str | list[str] | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class StatusCondition(BaseModel):
    equals: str | list[str] | None = None
    does_not_equal: str | list[str] | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class DateCondition(BaseModel):
    equals: str | None = None
    before: str | None = None
    after: str | None = None
    on_or_before: str | None = None
    on_or_after: str | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None
    this_week: dict | None = None
    past_week: dict | None = None
    past_month: dict | None = None
    past_year: dict | None = None
    next_week: dict | None = None
    next_month: dict | None = None
    next_year: dict | None = None


class PeopleCondition(BaseModel):
    contains: str | None = None
    does_not_contain: str | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class FilesCondition(BaseModel):
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class RelationCondition(BaseModel):
    contains: str | None = None
    does_not_contain: str | None = None
    is_empty: bool | None = None
    is_not_empty: bool | None = None


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    EXPIRED = "expired"
    NONE = "none"


class VerificationCondition(BaseModel):
    status: VerificationStatus


class FormulaCondition(BaseModel):
    string: TextCondition | None = None
    checkbox: CheckboxCondition | None = None
    number: NumberCondition | None = None
    date: DateCondition | None = None


class RollupCondition(BaseModel):
    any: Any | None = None
    none: Any | None = None
    every: Any | None = None
    date: DateCondition | None = None
    number: NumberCondition | None = None


class _PropertyFilterBase(BaseModel):
    """Base for all single-property filters."""

    property: str

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        result: dict[str, Any] = {"property": self.property}
        for field_name in type(self).model_fields:
            if field_name == "property":
                continue
            value = getattr(self, field_name)
            if value is not None:
                if isinstance(value, BaseModel):
                    result[field_name] = value.model_dump(exclude_none=True)
                else:
                    result[field_name] = value
        return result


class CheckboxFilter(_PropertyFilterBase):
    checkbox: CheckboxCondition


class DateFilter(_PropertyFilterBase):
    date: DateCondition


class FilesFilter(_PropertyFilterBase):
    files: FilesCondition


class FormulaFilter(_PropertyFilterBase):
    formula: FormulaCondition


class MultiSelectFilter(_PropertyFilterBase):
    multi_select: MultiSelectCondition


class NumberFilter(_PropertyFilterBase):
    number: NumberCondition


class PeopleFilter(_PropertyFilterBase):
    people: PeopleCondition


class PhoneNumberFilter(_PropertyFilterBase):
    phone_number: TextCondition


class RelationFilter(_PropertyFilterBase):
    relation: RelationCondition


class RichTextFilter(_PropertyFilterBase):
    rich_text: TextCondition


class SelectFilter(_PropertyFilterBase):
    select: SelectCondition


class StatusFilter(_PropertyFilterBase):
    status: StatusCondition


class UniqueIdFilter(_PropertyFilterBase):
    unique_id: NumberCondition


class VerificationFilter(_PropertyFilterBase):
    verification: VerificationCondition


PropertyFilter = Annotated[
    CheckboxFilter
    | DateFilter
    | FilesFilter
    | FormulaFilter
    | MultiSelectFilter
    | NumberFilter
    | PeopleFilter
    | PhoneNumberFilter
    | RelationFilter
    | RichTextFilter
    | SelectFilter
    | StatusFilter
    | UniqueIdFilter
    | VerificationFilter,
    Field(discriminator=None),
]


# ---------------------------------------------------------------------------
# Timestamp filters (no ``property`` field)
# ---------------------------------------------------------------------------


class TimestampType(StrEnum):
    CREATED_TIME = "created_time"
    LAST_EDITED_TIME = "last_edited_time"


class TimestampFilter(BaseModel):
    timestamp: TimestampType
    condition: DateCondition

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.value,
            self.timestamp.value: self.condition.model_dump(exclude_none=True),
        }


# ---------------------------------------------------------------------------
# Compound filters (and / or with nesting)
# ---------------------------------------------------------------------------


class CompoundFilter(BaseModel):
    and_: list[PropertyFilter | TimestampFilter | "CompoundFilter"] | None = Field(
        default=None, alias="and"
    )
    or_: list[PropertyFilter | TimestampFilter | "CompoundFilter"] | None = Field(
        default=None, alias="or"
    )

    model_config = {"populate_by_name": True}

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.and_ is not None:
            result["and"] = [_serialize_filter(f) for f in self.and_]
        if self.or_ is not None:
            result["or"] = [_serialize_filter(f) for f in self.or_]
        return result


CompoundFilter.model_rebuild()

type QueryFilter = PropertyFilter | TimestampFilter | CompoundFilter


def _serialize_filter(f: QueryFilter) -> dict[str, Any]:
    if isinstance(f, BaseModel):
        return f.model_dump(mode="json", by_alias=True)
    return f
