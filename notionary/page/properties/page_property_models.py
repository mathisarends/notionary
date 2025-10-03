from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, Field

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.shared.properties.property_type import PropertyType
from notionary.user.schemas import PersonUserResponseDto


class PageProperty(BaseModel):
    id: str
    type: str


class StatusOption(BaseModel):
    id: str
    name: str


class PageStatusProperty(PageProperty):
    id: str
    type: Literal[PropertyType.STATUS] = PropertyType.STATUS
    status: StatusOption | None = None
    options: list[StatusOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class RelationItem(BaseModel):
    id: str


class PageRelationProperty(PageProperty):
    type: Literal[PropertyType.RELATION] = PropertyType.RELATION
    relation: list[RelationItem] = Field(default_factory=list)
    has_more: bool = False


class PageURLProperty(PageProperty):
    type: Literal[PropertyType.URL] = PropertyType.URL
    url: str | None = None


class PageRichTextProperty(PageProperty):
    type: Literal[PropertyType.RICH_TEXT] = PropertyType.RICH_TEXT
    rich_text: list[RichText] = Field(default_factory=list)


class SelectOption(BaseModel):
    id: str
    name: str


class PageMultiSelectProperty(PageProperty):
    type: Literal[PropertyType.MULTI_SELECT] = PropertyType.MULTI_SELECT
    multi_select: list[SelectOption] = Field(default_factory=list)
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageSelectProperty(PageProperty):
    type: Literal[PropertyType.SELECT] = PropertyType.SELECT
    select: SelectOption | None = None
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PagePeopleProperty(PageProperty):
    type: Literal[PropertyType.PEOPLE] = PropertyType.PEOPLE
    people: list[PersonUserResponseDto] = Field(default_factory=list)


class DateValue(BaseModel):
    start: str
    end: str | None = None
    time_zone: str | None = None


class PageDateProperty(PageProperty):
    type: Literal[PropertyType.DATE] = PropertyType.DATE
    date: DateValue | None = None


class PageTitleProperty(PageProperty):
    type: Literal[PropertyType.TITLE] = PropertyType.TITLE
    title: list[RichText] = Field(default_factory=list)


class PageNumberProperty(PageProperty):
    type: Literal[PropertyType.NUMBER] = PropertyType.NUMBER
    number: float | None = None


class PageCheckboxProperty(PageProperty):
    type: Literal[PropertyType.CHECKBOX] = PropertyType.CHECKBOX
    checkbox: bool = False


class PageEmailProperty(PageProperty):
    type: Literal[PropertyType.EMAIL] = PropertyType.EMAIL
    email: str | None = None


class PagePhoneNumberProperty(PageProperty):
    type: Literal[PropertyType.PHONE_NUMBER] = PropertyType.PHONE_NUMBER
    phone_number: str | None = None


class PageCreatedTimeProperty(PageProperty):
    type: Literal[PropertyType.CREATED_TIME] = PropertyType.CREATED_TIME
    created_time: str | None = None


DiscriminatedPageProperty = Annotated[
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
    | PageCreatedTimeProperty,
    Field(discriminator="type"),
]

PagePropertyT = TypeVar("PagePropertyT", bound=PageProperty)
