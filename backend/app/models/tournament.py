from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))    # Grand Slam / Masters 1000 / ATP 500 ...
    surface: Mapped[str | None] = mapped_column(String(50))     # Hard / Clay / Grass
    location: Mapped[str | None] = mapped_column(String(200))
    start_date: Mapped[str | None] = mapped_column(Date)
    end_date: Mapped[str | None] = mapped_column(Date)
