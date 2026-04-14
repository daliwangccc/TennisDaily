from pydantic import BaseModel
from datetime import date


class RankingOut(BaseModel):
    id: int
    player_id: int
    player_name: str | None = None
    rank: int
    points: int = 0
    tour: str
    type: str = "singles"
    week_date: date | None = None

    model_config = {"from_attributes": True}


class RankingList(BaseModel):
    items: list[RankingOut]
    total: int
    tour: str
    type: str
