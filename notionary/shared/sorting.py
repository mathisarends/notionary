from enum import StrEnum


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortTimestamp(StrEnum):
    LAST_EDITED_TIME = "last_edited_time"
    CREATED_TIME = "created_time"
