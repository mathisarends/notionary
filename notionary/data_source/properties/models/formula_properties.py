from pydantic import BaseModel


class DataSourceFormulaConfig(BaseModel):
    expression: str


class DataSourceUniqueIdConfig(BaseModel):
    prefix: str | None = None
