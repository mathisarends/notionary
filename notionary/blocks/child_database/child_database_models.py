from typing import Literal
from pydantic import BaseModel


class ChildDatabaseBlock(BaseModel):
    title: str


class CreateChildDatabaseBlock(BaseModel):
    type: Literal["child_database"] = "child_database"
    child_database: ChildDatabaseBlock
