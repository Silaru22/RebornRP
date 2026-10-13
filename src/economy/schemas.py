from pydantic import BaseModel, ConfigDict, field_validator

from src.teable.schemas import TeableObjectLinkSchema


class FullTraderSchema(BaseModel):
    trader_id: str
    trader_serial: int
    classname: str
    trader_name: str
    role: str | None
    position: str
    orientation: str
    clothes: list[TeableObjectLinkSchema] | None

    category: str
    item: TeableObjectLinkSchema
    item_price: int
    item_buy_price: int
    max_stock: int
    coefficient: float
    trade_quantity: int

    @field_validator('item_price', mode='before')
    @classmethod
    def round_item_price(cls, v: float | str) -> int:
        return int(v)

    @field_validator('item_buy_price', mode='before')
    @classmethod
    def round_item_buy_price(cls, v: float | str) -> int:
        return int(v)


class StashesSchema(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    tier: str
    chancetoappear: str
    chancetoloot: str
    minspawncount: str
    maxspawncount: str
    mintimetoresetsearched: str
    maxtimetoresetsearched: str
    mintooldmg: str
    maxtooldmg: str


class StashLootSchema(BaseModel):
    tier: TeableObjectLinkSchema
    item: TeableObjectLinkSchema
    trade_quantity: int
