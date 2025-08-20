from typing import Literal

from pydantic import BaseModel


class BreadcrumbBlock(BaseModel):
    pass


class CreateBreadcrumbBlock(BaseModel):
    type: Literal["breadcrumb"] = "breadcrumb"
    breadcrumb: BreadcrumbBlock
