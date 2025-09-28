from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class NumberFormat(StrEnum):
    NUMBER = "number"
    NUMBER_WITH_COMMAS = "number_with_commas"
    PERCENT = "percent"
    DOLLAR = "dollar"
    AUSTRALIAN_DOLLAR = "australian_dollar"
    CANADIAN_DOLLAR = "canadian_dollar"
    SINGAPORE_DOLLAR = "singapore_dollar"
    EURO = "euro"
    POUND = "pound"
    YEN = "yen"
    RUBLE = "ruble"
    RUPEE = "rupee"
    WON = "won"
    YUAN = "yuan"
    REAL = "real"
    LIRA = "lira"
    RUPIAH = "rupiah"
    FRANC = "franc"
    HONG_KONG_DOLLAR = "hong_kong_dollar"
    NEW_ZEALAND_DOLLAR = "new_zealand_dollar"
    KRONA = "krona"
    NORWEGIAN_KRONE = "norwegian_krone"
    MEXICAN_PESO = "mexican_peso"
    RAND = "rand"
    NEW_TAIWAN_DOLLAR = "new_taiwan_dollar"
    DANISH_KRONE = "danish_krone"
    ZLOTY = "zloty"
    BAHT = "baht"
    FORINT = "forint"
    KORUNA = "koruna"
    SHEKEL = "shekel"
    CHILEAN_PESO = "chilean_peso"
    PHILIPPINE_PESO = "philippine_peso"
    DIRHAM = "dirham"
    COLOMBIAN_PESO = "colombian_peso"
    RIYAL = "riyal"
    RINGGIT = "ringgit"
    LEU = "leu"
    ARGENTINE_PESO = "argentine_peso"
    URUGUAYAN_PESO = "uruguayan_peso"
    PERUVIAN_SOL = "peruvian_sol"


class DataSourceNumberConfig(BaseModel):
    format: NumberFormat


class DataSourceNumberProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.NUMBER
    number: DataSourceNumberConfig = Field(default_factory=DataSourceNumberConfig)

    @property
    def number_format(self) -> str | None:
        return self.number.format
