from typing import Any

from pydantic import BaseModel, Field, model_serializer

from notionary.shared.properties.type import PropertyType


class PagePropertyDescription(BaseModel):
    """Normalized description of a single page property."""

    type: PropertyType | str
    current: Any = None
    options: list[str] = Field(default_factory=list)
    relation_options: list[str] = Field(default_factory=list)

    def __repr_args__(self) -> list[tuple[str, Any]]:
        args: list[tuple[str, Any]] = [("type", self.type), ("current", self.current)]
        if self.options:
            args.append(("options", self.options))
        if self.relation_options:
            args.append(("relation_options", self.relation_options))
        return args

    @model_serializer(mode="wrap")
    def _serialize(self, handler: Any) -> dict[str, Any]:
        data = handler(self)
        if not data.get("options"):
            data.pop("options", None)
        if not data.get("relation_options"):
            data.pop("relation_options", None)
        return data
