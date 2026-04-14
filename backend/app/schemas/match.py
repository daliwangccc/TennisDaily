from pydantic import BaseModel
from datetime import date


class MatchOut(BaseModel):
    id: int
    tournament_id: int | None = None
    player1_id: int | None = None
    player2_id: int | None = None
    player1_name: str | None = None
    player2_name: str | None = None
    winner_id: int | None = None
    score: str | None = None
    round: str | None = None
    surface: str | None = None
    match_date: date | None = None
    status: str = "finished"

    model_config = {"from_attributes": True}


class MatchDetail(MatchOut):
    stats: dict | None = None


class MatchList(BaseModel):
    items: list[MatchOut]
    total: int
    page: int
    page_size: int
