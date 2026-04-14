from pydantic import BaseModel
from datetime import date


class PlayerOut(BaseModel):
    id: int
    name_en: str
    name_cn: str | None = None
    country: str | None = None
    birth_date: date | None = None
    hand: str | None = None
    height_cm: int | None = None

    model_config = {"from_attributes": True}


class PlayerDetail(PlayerOut):
    backhand: str | None = None
    turned_pro: int | None = None
    coach: str | None = None
    photo_url: str | None = None
