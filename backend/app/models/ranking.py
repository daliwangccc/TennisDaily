from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    player_name: Mapped[str | None] = mapped_column(String(200))
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    tour: Mapped[str] = mapped_column(String(10), nullable=False)     # ATP / WTA
    type: Mapped[str] = mapped_column(String(20), default="singles")  # singles / doubles
    week_date: Mapped[str | None] = mapped_column(Date)
