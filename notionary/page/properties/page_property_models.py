from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.shared.models.shared_property_models import PropertyType
from notionary.shared.models.user_models import NotionUser


class IgnoreExtraFieldsMixin(BaseModel):
    model_config = ConfigDict(extra="ignore")


class SelectOption(BaseModel):
    id: str
    name: str


class StatusOption(BaseModel):
    id: str
    name: str


class RelationItem(BaseModel):
    id: str


class DateValue(BaseModel):
    start: str
    end: str | None = None
    time_zone: str | None = None


class PageStatusProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.STATUS
    status: StatusOption | None = None
    options: list[StatusOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageRelationProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.RELATION
    relation: list[RelationItem] = Field(default_factory=list)
    has_more: bool = False


class PageURLProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.URL
    url: str | None = None


class PageRichTextProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: list[RichTextObject] = Field(default_factory=list)


class PageMultiSelectProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: list[SelectOption] = Field(default_factory=list)
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageSelectProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.SELECT
    select: SelectOption | None = None
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PagePeopleProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.PEOPLE
    people: list[NotionUser] = Field(default_factory=list)


class PageDateProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.DATE
    date: DateValue | None = None


class PageTitleProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.TITLE
    title: list[RichTextObject] = Field(default_factory=list)


class PageNumberProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.NUMBER
    number: float | None = None


class PageCheckboxProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: bool = False


class PageEmailProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.EMAIL
    email: str | None = None


class PagePhoneNumberProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: str | None = None


class PageCreatedTimeProperty(IgnoreExtraFieldsMixin):
    id: str
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: str | None = None


# ===== TYPE UNIONS =====
PageProperty = (
    PageStatusProperty
    | PageRelationProperty
    | PageURLProperty
    | PageRichTextProperty
    | PageMultiSelectProperty
    | PageSelectProperty
    | PagePeopleProperty
    | PageDateProperty
    | PageTitleProperty
    | PageNumberProperty
    | PageCheckboxProperty
    | PageEmailProperty
    | PagePhoneNumberProperty
    | PageCreatedTimeProperty
    | dict[str, Any]  # Fallback
)

PagePropertyT = TypeVar("PagePropertyT", bound=PageProperty)
