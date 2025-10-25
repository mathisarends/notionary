from enum import StrEnum
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.rich_text.models import RichText
from notionary.shared.models.file import File
from notionary.shared.properties.type import PropertyType
from notionary.shared.typings import JsonDict
from notionary.user.schemas import PersonUserResponseDto, UserResponseDto

# ============================================================================
# Base Models
# ============================================================================


class PageProperty(BaseModel):
    id: str
    type: str


class StatusOption(BaseModel):
    id: str
    name: str


class SelectOption(BaseModel):
    id: str | None = None
    name: str


class RelationItem(BaseModel):
    id: str


class DateValue(BaseModel):
    start: str
    end: str | None = None
    time_zone: str | None = None


# ============================================================================
# Formula Models
# ============================================================================


class FormulaValueType(StrEnum):
    BOOLEAN = "boolean"
    DATE = "date"
    NUMBER = "number"
    STRING = "string"


class FormulaValue(BaseModel):
    type: FormulaValueType
    boolean: bool | None = None
    date: DateValue | None = None
    number: float | None = None
    string: str | None = None


# ============================================================================
# Rollup Models
# ============================================================================


class RollupValueType(StrEnum):
    NUMBER = "number"
    DATE = "date"
    ARRAY = "array"
    INCOMPLETE = "incomplete"
    UNSUPPORTED = "unsupported"


class RollupValue(BaseModel):
    type: RollupValueType
    function: str  # e.g., "sum", "count", "average", "max", "min", etc.
    number: float | None = None
    date: DateValue | None = None
    array: list[Any] | None = None


# ============================================================================
# Unique ID Models
# ============================================================================


class UniqueIdValue(BaseModel):
    number: int  # Auto-incrementing count
    prefix: str | None = None  # Optional prefix like "RL"


# ============================================================================
# Verification Models
# ============================================================================


class VerificationState(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


class VerificationValue(BaseModel):
    state: VerificationState
    verified_by: UserResponseDto | None = None
    date: DateValue | None = None  # start = verification date, end = expiration


# ============================================================================
# Page Property Classes
# ============================================================================


class PageTitleProperty(PageProperty):
    type: Literal[PropertyType.TITLE] = PropertyType.TITLE
    title: list[RichText] = Field(default_factory=list)


class PageRichTextProperty(PageProperty):
    type: Literal[PropertyType.RICH_TEXT] = PropertyType.RICH_TEXT
    rich_text: list[RichText] = Field(default_factory=list)


class PageSelectProperty(PageProperty):
    type: Literal[PropertyType.SELECT] = PropertyType.SELECT
    select: SelectOption | None = None
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageMultiSelectProperty(PageProperty):
    type: Literal[PropertyType.MULTI_SELECT] = PropertyType.MULTI_SELECT
    multi_select: list[SelectOption] = Field(default_factory=list)
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageStatusProperty(PageProperty):
    type: Literal[PropertyType.STATUS] = PropertyType.STATUS
    status: StatusOption | None = None
    options: list[StatusOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageNumberProperty(PageProperty):
    type: Literal[PropertyType.NUMBER] = PropertyType.NUMBER
    number: float | None = None


class PageDateProperty(PageProperty):
    type: Literal[PropertyType.DATE] = PropertyType.DATE
    date: DateValue | None = None


class PageCheckboxProperty(PageProperty):
    type: Literal[PropertyType.CHECKBOX] = PropertyType.CHECKBOX
    checkbox: bool = False


class PageURLProperty(PageProperty):
    type: Literal[PropertyType.URL] = PropertyType.URL
    url: str | None = None


class PageEmailProperty(PageProperty):
    type: Literal[PropertyType.EMAIL] = PropertyType.EMAIL
    email: str | None = None


class PagePhoneNumberProperty(PageProperty):
    type: Literal[PropertyType.PHONE_NUMBER] = PropertyType.PHONE_NUMBER
    phone_number: str | None = None


class PagePeopleProperty(PageProperty):
    type: Literal[PropertyType.PEOPLE] = PropertyType.PEOPLE
    people: list[PersonUserResponseDto] = Field(default_factory=list)


class PageCreatedByProperty(PageProperty):
    type: Literal[PropertyType.CREATED_BY] = PropertyType.CREATED_BY
    created_by: UserResponseDto


class PageLastEditedByProperty(PageProperty):
    type: Literal[PropertyType.LAST_EDITED_BY] = PropertyType.LAST_EDITED_BY
    last_edited_by: UserResponseDto


class PageCreatedTimeProperty(PageProperty):
    type: Literal[PropertyType.CREATED_TIME] = PropertyType.CREATED_TIME
    created_time: str


class PageLastEditedTimeProperty(PageProperty):
    type: Literal[PropertyType.LAST_EDITED_TIME] = PropertyType.LAST_EDITED_TIME
    last_edited_time: str


class PageLastVisitedTimeProperty(PageProperty):
    type: Literal[PropertyType.LAST_VISITED_TIME] = PropertyType.LAST_VISITED_TIME
    last_visited_time: str | None = None


class PageFormulaProperty(PageProperty):
    type: Literal[PropertyType.FORMULA] = PropertyType.FORMULA
    formula: FormulaValue


class PageRollupProperty(PageProperty):
    type: Literal[PropertyType.ROLLUP] = PropertyType.ROLLUP
    rollup: RollupValue


class PageFilesProperty(PageProperty):
    type: Literal[PropertyType.FILES] = PropertyType.FILES
    files: list[File] = Field(default_factory=list)


class PageRelationProperty(PageProperty):
    type: Literal[PropertyType.RELATION] = PropertyType.RELATION
    relation: list[RelationItem] = Field(default_factory=list)
    has_more: bool = False


class PageButtonProperty(PageProperty):
    type: Literal[PropertyType.BUTTON] = PropertyType.BUTTON
    button: JsonDict = Field(default_factory=dict)


class PageLocationProperty(PageProperty):
    type: Literal[PropertyType.LOCATION] = PropertyType.LOCATION
    location: JsonDict | None = None


class PagePlaceProperty(PageProperty):
    type: Literal[PropertyType.PLACE] = PropertyType.PLACE
    place: JsonDict | None = None


class PageVerificationProperty(PageProperty):
    type: Literal[PropertyType.VERIFICATION] = PropertyType.VERIFICATION
    verification: VerificationValue


class PageUniqueIdProperty(PageProperty):
    type: Literal[PropertyType.UNIQUE_ID] = PropertyType.UNIQUE_ID
    unique_id: UniqueIdValue


class PageUnknownProperty(PageProperty):
    model_config = ConfigDict(extra="allow")


type AnyPageProperty = (
    PageTitleProperty
    | PageRichTextProperty
    | PageSelectProperty
    | PageMultiSelectProperty
    | PageStatusProperty
    | PageNumberProperty
    | PageDateProperty
    | PageCheckboxProperty
    | PageURLProperty
    | PageEmailProperty
    | PagePhoneNumberProperty
    | PagePeopleProperty
    | PageCreatedByProperty
    | PageLastEditedByProperty
    | PageCreatedTimeProperty
    | PageLastEditedTimeProperty
    | PageLastVisitedTimeProperty
    | PageFormulaProperty
    | PageRollupProperty
    | PageFilesProperty
    | PageRelationProperty
    | PageButtonProperty
    | PageLocationProperty
    | PagePlaceProperty
    | PageVerificationProperty
    | PageUniqueIdProperty
    | PageUnknownProperty
)

PagePropertyT = TypeVar("PagePropertyT", bound=PageProperty)
