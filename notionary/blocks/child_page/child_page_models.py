from typing import Literal
from pydantic import BaseModel


class ChildPageBlock(BaseModel):
    title: str
    
    
class CreateChildPageBlock(BaseModel):
    type: Literal["child_page"] = "child_page"
    child_page: ChildPageBlock