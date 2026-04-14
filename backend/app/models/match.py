from sqlalchemy import Integer, String, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tournaments.id"))
    player1_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"))
    player2_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"))
    winner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"))
    score: Mapped[str | None] = mapped_column(String(200))        # e.g. "6-4, 3-6, 7-5"
    round: Mapped[str | None] = mapped_column(String(50))         # Final / SF / QF / R16 ...
    surface: Mapped[str | None] = mapped_column(String(50))
    match_date: Mapped[str | None] = mapped_column(Date)
    stats: Mapped[dict | None] = mapped_column(JSON)              # aces, double faults, etc.
    status: Mapped[str] = mapped_column(String(20), default="finished")  # scheduled / live / finished
    player1_name: Mapped[str | None] = mapped_column(String(200))
    player2_name: Mapped[str | None] = mapped_column(String(200))
