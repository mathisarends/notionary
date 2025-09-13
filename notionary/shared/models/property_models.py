from __future__ import annotations
from enum import StrEnum

from pydantic import BaseModel


class PropertyType(StrEnum):
    """Enum for property types used in NotionPage."""

    SELECT = "select"
    MULTI_SELECT = "multi_select"
    STATUS = "status"
    RELATION = "relation"
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"


class SelectOption(BaseModel):
    """Model for select/multi_select/status options."""
    model_config = ConfigDict(extra="allow")
    
    name: str
    id: str | None = None