from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class DataSourceTitleConfig(BaseModel): ...


class DataSourceRichTextConfig(BaseModel): ...


class DataSourceURLConfig(BaseModel): ...


class DataSourceTitleProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.TITLE
    title: DataSourceTitleConfig = Field(default_factory=DataSourceTitleConfig)


class DataSourceRichTextProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: DataSourceRichTextConfig = Field(default_factory=DataSourceRichTextConfig)


class DataSourceURLProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.URL
    url: DataSourceURLConfig = Field(default_factory=DataSourceURLConfig)
